import json
import numpy as np
import time

from copy import deepcopy

import labrad

from experiments import Scan, Loop

""" parameters here """
name = 'clock_lock'

zero_freq = 27.8678e6
center_shift = -82.9
zeeman_shift = 263.75

linewidth = 18.4
linewidth = 2
modulation_depth = linewidth / 2.

Tpi = 0.055
Tpi2 = Tpi / 2

sampling_period = 14.6 * 4
peak_height1 = 1
peak_height2 = 1


overall_gain = 1
prop_gain = .0
int_gain = 0.28
diff_gain = .0 

intint_gain = .05

""" should not regularly need to change stuff below here """
lock_points = [
    ['-9/2', 'left'], 
    ['+9/2', 'left'], 
    ['-9/2', 'right'],
    ['+9/2', 'right'],
]

DATA_DIR = '/home/srgang/yesrdata/SrQ/data/{}/'.format(time.strftime('%Y%m%d'))

sequence = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'evaporate',
    'load_lattice',
    'rabi_clock-pi',
    'clean_g',
#    'rabi_clock', 
    'ramsey_clock', 
    'image_clock',
]

readout_type = 'camera'
camera_settings = {
    'camera_name': 'andor',
    'processor_type': 'process_eg',
    'offset': (515, 195),
    'size': (200, 200),
    'roi': {
        'center': [15, 15, 0, 0],
        },
    'norm': (0, 0, 60, 80),
    'pulse_length': 5,
    }

dither_lock_config = {
    "-9/2": {
        "pid": {
            'overall_gain': overall_gain / peak_height1 * linewidth,
            'prop_gain': prop_gain,
            'int_gain': int_gain / sampling_period,
            'intint_gain': intint_gain / sampling_period**2,
            'diff_gain': diff_gain * sampling_period,
            'sampling_period': sampling_period,
            'output': zero_freq - center_shift + zeeman_shift,
            'output_offset': zero_freq - center_shift + zeeman_shift,
            'readout_type': readout_type,
            'camera_settings': camera_settings,
        },
        'dither': {
            'modulation_depth': modulation_depth,
        },
    },
    "+9/2": {
        "pid": {
            'overall_gain': overall_gain / peak_height2 * linewidth,
            'prop_gain': prop_gain,
            'int_gain': int_gain / sampling_period,
            'intint_gain': intint_gain / sampling_period**2,
            'diff_gain': diff_gain * sampling_period,
            'sampling_period': sampling_period,
            'output': zero_freq - center_shift - zeeman_shift,
            'output_offset': zero_freq - center_shift - zeeman_shift,
            'readout_type': readout_type,
            'camera_settings': camera_settings,
        },
        'dither': {
            'modulation_depth': modulation_depth,
        },
    },
}

parameters = {
    'clock_servo': {
        'dither_lock': dither_lock_config,
        },
    '+9/2': {
        'frequency': {},
        },
    '-9/2': {
        'frequency': {},
        },
}

parameter_values = {
    'clock_servo': {
        'dither_lock': [
            {
                'pid': lock_points[i-2],
                'dither': lock_points[i],
            }
            for i in range(len(lock_points))]
        },
    'sequencer': {
        'sequence': sequence,
        '*Trabi': .8 / linewidth,
        '*Tramsey': .5 / linewidth,
        '*Tpi': Tpi,
        '*Tpi2':Tpi2,
        },
    'plotter': {
        'plot': {
#            'plotter_path': DATA_DIR + 'notebooks\\helpers2.py',
            'plotter_path': DATA_DIR + 'notebooks/helpers2.py',
            'plotter_function': 'plot_clock_lock2',
            'args': [DATA_DIR + name, zero_freq + center_shift],
            'kwargs': {},
            },
        },
    "andor": {
        "recorder": {},
        "image_path": None,
        },    
    }

init_parameter_values = deepcopy(parameter_values)
for value in init_parameter_values['clock_servo']['dither_lock']:
    value['pid'] = []

print init_parameter_values
print 
print parameter_values

cxn = labrad.connect()
c = cxn.conductor
# cannot register parameter if already registered. 
# but we net to change config...
for parameter_name, parameter in parameters.items():
    try:
        c.remove_parameters(json.dumps({parameter_name: parameter}))
    except:
        print parameter_name, 'not unregistered'

c.register_parameters(json.dumps(parameters))

#init = Scan(
#    name='clock_lock',
#    parameter_values=init_parameter_values,
#)
loop = Loop(
    name='clock_lock',
    parameter_values=parameter_values,
    append_data=True
)
#init.queue(clear_all=True)
loop.queue(clear_all=True)
