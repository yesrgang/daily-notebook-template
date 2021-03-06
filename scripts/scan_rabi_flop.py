from experiments import *
import time

name = 'scan_rabi_flop'

zero_freq = 28.0482e6
center_shift = 25
zeeman_shift_abs = 2.3699e3

rabi_guess = 2e-3
t_start = 0.0
t_stop = rabi_guess * 5
n_point = 40
Tpi = 2e-3

clock_intensity = -3.5

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
#sequence_type = 'fast'

if sequence_type =='fast':
    HODTi = -0.1
    VODTi = -.05
    VODTm = -.05
    VODTf = -.05
elif sequence_type == 'slow':
    HODTi = -1.2
    VODTi = -1.2
    HODTf = -0.06
    VODTf = -0.2
else:
    HODTi = -1.2
    HODTf = -0.06
    VODTi = -1.2
    VODTm = -0.2
    VODTf = -0.2


""" should not need to regularly change stuff below here """
try:
    Tpi
except:
    Tpi = rabi_guess
FAST_SEQUENCE = [
    'blue_mot',
    'red_mot-fast',
    'load_odt-fast',
    'load_lattice-fast',
#    'polarize_m-lat',
    'polarize_p-lat',
    'rabi_clock-pi-fast',
    'clean_g',
    'rabi_clock-fast',
#    'pmt-fast',
    'pmt-fast-v',
    ]

SLOW_SEQUENCE = [
    'blue_mot',
    'red_mot',
    'load_odt',
    'depolarize',
    'anti_polarize',
    'evaporate',
    'load_lattice',
#    'rabi_clock-pi',
#    'clean_g',
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
#    'hold_lattice',
    'rabi_clock-pi',
    'clean_g',
    'rabi_clock',
    'image_clock',
    ]

if sequence_type == 'fast':
    SEQUENCE = FAST_SEQUENCE
elif sequence_type == 'slow':
    SEQUENCE = SLOW_SEQUENCE
else:
    SEQUENCE = CAMERA_SEQUENCE

if probe_type == 'nobias':
    if 'anti_polarize' in SEQUENCE:
        SEQUENCE.remove('anti_polarize')

center_freq = zero_freq - center_shift - zeeman_shift
print center_freq

times = np.linspace(t_start, t_stop, n_point+1).tolist()[1:]
DATA_DIR = '/home/srgang/yesrdata/SrQ/data/{}/'.format(time.strftime('%Y%m%d'))

parameter_values = {
    'clock_aom': {
        'frequency': center_freq,
#        'frequency2': center_freq,
        'frequency3': center_freq,
        'center_frequency': center_freq,
    },
    'sequencer': {
        'sequence': SEQUENCE,        
        '*Trabi': times,
        '*Tpi': Tpi,
        '*Iclk': clock_intensity,
    },
    'plotter': {
        'plot': {
            'plotter_path': DATA_DIR + 'notebooks/helpers2.py',
            'plotter_function': 'plot_rabi_flop',
            'args': [],
            'kwargs': {},
        },
    },

}
if sequence_type == 'fast':
#    parameter_values['sequencer']['sequence'] = FAST_SEQUENCE
    parameter_values['sequencer']['*T_bm'] = .8
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTi'] = VODTi
    parameter_values['sequencer']['*VODTm'] = VODTi
    parameter_values['sequencer']['*HODTf'] = HODTi
    parameter_values['sequencer']['*VODTf'] = VODTi

elif sequence_type == 'slow':
#    parameter_values['sequencer']['sequence'] = SLOW_SEQUENCE
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTf'] = VODTf
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTm'] = VODTi
    parameter_values['sequencer']['*VODTi'] = VODTi
else:
    parameter_values['sequencer']['*T_bm'] = 2.5
    parameter_values['sequencer']['*HODTf'] = HODTf
    parameter_values['sequencer']['*VODTf'] = VODTf
    parameter_values['sequencer']['*VODTm'] = VODTm
    parameter_values['sequencer']['*HODTi'] = HODTi
    parameter_values['sequencer']['*VODTi'] = VODTi
    parameter_values['plotter']['plot']['plotter_function'] = 'plot_clock_camera'

parameters = {
}

scan = Scan(
    name=name,
    parameter_values=parameter_values,
)

scan.queue(clear_all=True)# True:clear the queue
