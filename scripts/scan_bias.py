from experiments import *
import time

name = 'scan_bias'

""" 
H clock:
    NDX: rabi_time, intensity for pi pulse  
    ND0: 3.5e-3, -6 unpol (updated)
    ND2: 13.5e-3, -3.5
    ND2: 20e-3, -6 unpol (updated)
    ND3: 25e-3, -3.5 unpol
    ND4: 32.5e-3, -3.5 
    ND4: 60e-3, -6 unpol (updated)
    ND5: 100e-3, -3.5 roughly
    ND6: 220e-3, -3.5 fast pol

    ND9: 6, -1.5 seems about right
    
    mF = 1/2:
    ND0: 22e-3, -6 for +/- 1/2

    ND2: 130e-3, -6

V clock:
    ND0: 250e-6, all power: 5mW, unpol (updated)
    1mW: 1.0e-3, unpol (update)
"""

#zero_freq = 27.864335e6
#center_shift = 2.71e3


zero_freq = 27.864895e6
center_shift = -4 

zeeman_shift_abs = 2.372e3
rabi_time = 35e-3 * 5
clock_intensity = -1.

scan_direction = '*XCCclk'
bias_fields = {
    '*XCCclk': 0.58, 
    '*YCCclk': 0.23, 
    '*ZCCclk': -0.0085, 
    }
bias_range = .4
steps = 20

sequence_type = 'camera'

""" probe settings """


""" sequencer parameters """

if sequence_type =='fast':
    HODTi = -.2 #2.0
    VODTi = -0.2 #0.6*Tpi
elif sequence_type == 'slow':
    HODTi = -1.2
    VODTi = -1.2
    HODTf = -0.06
    VODTf = -0.4
else:
    HODTi = -1.4
    HODTf = -0.054
    VODTi = -1.4
    VODTf = -0.4


""" should not need to regularly change stuff below here """
FAST_SEQUENCE = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'load_lattice',
    'rabi_clock',
    'pmt',
]

SLOW_SEQUENCE = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'evaporate',
    'load_lattice',
    'rabi_clock',
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
    'rabi_clock',
    'image_clock',
    ]

if sequence_type == 'fast':
    SEQUENCE = FAST_SEQUENCE
elif sequence_type == 'slow':
    SEQUENCE = SLOW_SEQUENCE
else:
    SEQUENCE = CAMERA_SEQUENCE


center_freq = zero_freq - center_shift

XCCclk = bias_fields['*XCCclk']
YCCclk = bias_fields['*YCCclk']
ZCCclk = bias_fields['*ZCCclk']

if scan_direction == '*XCCclk':
    XCCclk = XCCclk + np.linspace(-bias_range, 
            bias_range, steps)
if scan_direction == '*YCCclk':
    YCCclk = YCCclk + np.linspace(-bias_range, 
            bias_range, steps)
if scan_direction == '*ZCCclk':
    ZCCclk = ZCCclk + np.linspace(-bias_range, 
            bias_range, steps)

print XCCclk
print YCCclk
print ZCCclk
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
        '*Trabi': rabi_time,
        '*XCCclk': XCCclk,
        '*YCCclk': YCCclk,
        '*ZCCclk': ZCCclk,
        '*Iclk': clock_intensity,
        '*Tpi': rabi_time,
    },
    "andor": {
        "recorder": {},
        "image_path": None,
        },
    }

if sequence_type == 'fast':
    parameter_values['sequencer']['*T_bm'] = .3
    parameter_values['sequencer']['*HODTf'] = HODTi
    parameter_values['sequencer']['*VODTf'] = VODTi
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTi'] = VODTi
elif sequence_type == 'slow':
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTf'] = VODTf
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTi'] = VODTi
elif sequence_type == 'camera':
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTf'] = VODTf
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTi'] = VODTi


parameters = {
}

scan = Scan(
    name=name,
    parameter_values=parameter_values,
    append_data=0,
)

scan.queue(clear_all=1)
#for i in range(queue_length - 1):
#    scan.queue(clear_all=0)
