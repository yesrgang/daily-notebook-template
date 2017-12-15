from experiments import *
import time

name = 'scan_slosh'
camera = 'Mako2'
arm = 'h1'
axis = 'y'

positions = {
    'h1x': 30,
    'h1y': 47,
    'h2x': 50,
    'h2y': 90,
    }


Ti = 1e-5
if axis == 'y':
    Tf = 14e-3
    Tkick = 400e-6
    wait_times = np.linspace(Ti, Tf, 16)
if axis == 'y':
# HODTf .25
    Tf = 7e-3
    Tkick = 400e-6
    wait_times = np.linspace(Ti, Tf, 16)
elif axis == 'x':
    Tf = 50e-3
    Tkick = 2e-3
    wait_times = np.linspace(Ti, Tf, 16)


key = arm + axis
DATA_DIR = '/home/srgang/yesrdata/SrQ/data/{}/'.format(time.strftime('%Y%m%d'))
parameter_values = {    
#        'lattice_piezo': {key: positions[key]},
        'lattice_piezo': positions,
        'sequencer': {
            '*Tslosh': wait_times,
            '*HODTf': -.25,#-0.15
            '*VODTf': -.4,#-0.2
            '*Tkick': Tkick,
            'sequence': [
                'blue_mot',
                'red_mot',
                'load_odt',
                'depolarize',
#                'anti_polarize',
                'evaporate',
                'lattice_kick_tof',
                'image',
            ],
        },
        'plotter': {
            'plot': {
                'plotter_path': DATA_DIR + 'notebooks/helpers2.py',
                'plotter_function': 'plot_scan_slosh',
                'args': [DATA_DIR+ name],
                'kwargs': {'camera': camera},
            },
        },
    }
print positions

parameters = {}

scan = Scan(
    name=name,
    parameter_values=parameter_values,
    append_data=0,

    )

import labrad
cxn = labrad.connect()
cxn.sequencer.channel_manual_output('813 H1 Shutter', False)
cxn.sequencer.channel_manual_output('813 H2 Shutter', False)
cxn.sequencer.channel_manual_output('813 V Shutter', False)

if arm == 'h1':
    cxn.sequencer.channel_mode('813 H1 Shutter', 'auto')
    cxn.sequencer.channel_mode('813 H2 Shutter', 'manual')
    cxn.sequencer.channel_mode('813 V Shutter', 'manual')
elif arm == 'h2':
    cxn.sequencer.channel_mode('813 H1 Shutter', 'manual')
    cxn.sequencer.channel_mode('813 H2 Shutter', 'auto')
    cxn.sequencer.channel_mode('813 V Shutter', 'manual')

scan.queue(clear_all=1)# True:clear the queue
