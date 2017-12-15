from experiments import *
import time

name = 'scan_red_imaging'

v_center = -.04
v_range = .15
num_points = 40

v = np.linspace(v_center - v_range, v_center + v_range, num_points)

SEQUENCE = [
    'blue_mot',
    'red_mot-fast',     
    'load_odt-fast',
    'tof',
    'image_red',
]

SEQUENCE = [
    'blue_mot',
    'red_mot-fast',     
    'load_odt-fast',
    'load_lattice-fast',
    'tof-lat',
    'image_red-lat',
]

parameter_values = {
    'sequencer': {
        'sequence': SEQUENCE,
        '*beta_img': v,
        },

    }

parameters = {
}

scan = Scan(
    name=name,
    parameter_values=parameter_values,
    append_data=0,
)

scan.queue(clear_all=1)
