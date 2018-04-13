from experiments import *
import time

name = 'scan_clock'

zero_freq = 28.0482e6
center_shift = 24
zeeman_shift_abs = 2.3699e3
""" rabi times
Iclk = -7:
    ND0: 2e-3
    ND2: 10.5e3
    ND4: 51e-3
    ND6: 400e-3
    ND7: 1.
"""

rabi_time = 2.25e-3
#rabi_time = 400e-3
ramsey_time = .5 / 2
do_scan = True

Tpi = 2.25e-3
Tpi2 = Tpi / 2.

clock_intensity = -3.1

#projection = .5:
queue_length = 1
probe_type = 'bias_p'
sequence_type = 'fast'

""" probe settings """

if probe_type == 'bias': # don't edit this line!
    zeeman_shift = 0
    bias_field = -9.0
if probe_type == 'bias_m': # don't edit this line!
    zeeman_shift = -zeeman_shift_abs
    bias_field = -9.0
elif probe_type == 'bias_p':
    zeeman_shift = zeeman_shift_abs
    bias_field = -9.0
elif probe_type == 'nobias':
    zeeman_shift = 0
    bias_field = -0.0085
elif probe_type == 'sideband':
    zeeman_shift = 0
    bias_field = -0.0085
    center_shift = center_shift

""" sequencer parameters """
if sequence_type =='fast':
    HODTi = -.12 #-.08
    VODTi = -.05
    VODTm = -.05
    VODTf = -.05
elif sequence_type == 'slow':
    HODTi = -1.2
    HODTf = -0.06
    VODTi = -1.2
    VODTm = -.4
    VODTf = -0.4
else:
    HODTi = -1.2
    HODTf = -0.06
    VODTi = -1.2
    VODTm = -0.2
    VODTf = -0.2


""" should not need to regularly change stuff below here """

FAST_SEQUENCE = [
    'blue_mot',
    'red_mot-fast',
    'load_odt-fast',
#    'depolarize',
    'load_lattice-fast',
#    'polarize_m-lat',
    'polarize_p-lat',
#    'rabi_clock-pi-fast',
#    'clean_g',
    'rabi_clock-fast',
#    'pmt-fast',
    'pmt-fast-v',
#    'image_clock',
    ]

FAST_SEQUENCE = [
    'blue_mot',
    'red_mot-fast',
    'load_odt-fast',
#    'depolarize',
    'load_lattice-fast',
#    'polarize_m-lat',
    'polarize_p-lat',
    'rabi_clock-pi-fast',
    'clean_g',
    'ramsey-prep',
    'ramsey-pi2',
    'ramsey-dark',
    'ramsey-pi-180',
    'ramsey-dark',
#    'ramsey-pi-90',
#    'ramsey-dark',
#    'ramsey-pi-0',
#    'ramsey-dark',
#    'ramsey-pi-270',
#    'ramsey-dark',
#    'ramsey-pi-180',
#    'ramsey-dark',
    'ramsey-pi2-final',
#    'pmt-fast',
    'pmt-fast-v',
#    'image_clock',
    ]


SLOW_SEQUENCE = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'evaporate',
    'load_lattice',
    'rabi_clock-pi',
    'clean_g',
#    'hold_lattice',
    'rabi_clock',
#    'ramsey_clock',
    'pmt',
]

CAMERA_SEQUENCE = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'evaporate',
    'load_lattice',
#    'rabi_clock-pi',
#    'clean_g',
#    'rabi_clock',
    'ramsey_clock',
    'image_clock',
    ]

if sequence_type == 'fast':
    SEQUENCE = FAST_SEQUENCE
elif sequence_type == 'slow':
    SEQUENCE = SLOW_SEQUENCE
else:
    SEQUENCE = CAMERA_SEQUENCE

#if probe_type == 'nobias':
#    if 'anti_polarize' in SEQUENCE:
#        SEQUENCE.remove('anti_polarize')

try:
    linewidth
except:
    if 'ramsey_clock' in SEQUENCE:
        print 'Ramsey!'
        linewidth = 0.5/ramsey_time
    elif 'ramsey-pi2' in SEQUENCE:
        print 'Ramsey!'
        linewidth = 0.5/ramsey_time
    else:
        linewidth = .8/rabi_time

print "linewidth: ", linewidth

center_freq = zero_freq - center_shift - zeeman_shift

degrees = np.linspace(-180, 180, 20).tolist()
degrees.append(180)
phases = 5 / 180. * np.array(degrees)
#phases = np.ones(100) * 2.5
print phases

DATA_DIR = '/home/srgang/yesrdata/SrQ/data/{}/'.format(time.strftime('%Y%m%d'))

parameter_values = {
    'clock_aom': {
        'frequency': center_freq,
        'center_frequency': center_freq,
    },
    'clock_servo': {
        'dither_lock': {},
    },
    'sequencer': {
        'sequence': SEQUENCE,
#        '*Trabi': rabi_times,
        '*XCCclk': 0.78,
        '*YCCclk': 0.24,
        '*ZCCclk': bias_field,
        '*Iclk': clock_intensity,
        '*Tpi': Tpi,
        '*Tpi2': Tpi2,
        '*Tramsey': ramsey_time,
        '*clock-phase': phases,
    },
    'plotter': {
        'plot': {
            'plotter_path': DATA_DIR + 'notebooks/helpers2.py',
            'plotter_function': 'plot_clock_scan',
            'args': [center_freq],
            'kwargs': {'units': 'Hz'},
        },
    },
}

if sequence_type == 'fast':
    parameter_values['sequencer']['*T_bm'] = .8
    parameter_values['sequencer']['*HODTf'] = HODTi
    parameter_values['sequencer']['*VODTf'] = VODTi
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTm'] = VODTm
    parameter_values['sequencer']['*VODTi'] = VODTi
elif sequence_type == 'slow':
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTi'] = VODTi
    parameter_values['sequencer']['*VODTm'] = VODTm
    parameter_values['sequencer']['*VODTf'] = VODTf
elif sequence_type == 'camera':
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTf'] = VODTf
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTm'] = VODTm
    parameter_values['sequencer']['*VODTi'] = VODTi

    parameter_values['plotter']['plot']['plotter_function'] = 'plot_clock_camera'

parameters = {
}

scan = Scan(
    name=name,
    parameter_values=parameter_values,
    append_data=0,
)

scan.queue(clear_all=1)
for i in range(queue_length-1):
    scan.queue(clear_all=0)
