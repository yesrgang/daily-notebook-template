import labrad
import json

T_bm = 3

HODTi = -2.0
HODTf = -0.2
VODTi = -0.6 # -0.6
VODTm = -.1 #-0.3
VODTf = -.1 # -.03

#T_bm = .4
#HODTi = -.25
#VODTi = -.2 # -0.6
#VODTm = -.2 #-0.3
#VODTf = -.2 # -.03

sequence = [
    'blue_mot',
#    'rm_tof',
#    'rm_tof-fast',
#    'red_mot-fast',     
    'red_mot',     
#    'load_odt-fast',
#    'load_odt',
     'load_odt_trans',
#    'load_odt_tof',
#    'depolarize',
#    'anti_polarize', 
#    'evaporate',
#    'load_lattice-fast',
#    'load_lattice',
#    'load_lattice-test',
#    'unload_lattice-test',
#    'rabi_clock',
#    'tof-lat',
    'tof',
#    'find_trans',
    'image',
#    'image_red',
#    'image_ft',
#    'image_clock',
#    'pmt'
]
#T_bm = 1
#HODTi = -0.09
#HODTf = -0.09
#VODTi = -0.05 # -0.6
#VODTm = -.05 #-0.3
#VODTf = -.05 # -.03
#sequence = [
#    'blue_mot',
#    'red_mot-fast',     
#    'load_odt-fast',
#    'tof',
#    'image',
#]

#sequence = ['blue_blink']*40
#sequence = ['habs-blink']*40
#sequence = ['rabi_clock-test']*20
#sequence = ['test']

""" should not regularly need to change stuff below here """
if 'evaporate' not in sequence:
    HODTf = HODTi
    VODTf = VODTi

parameter_values = {
    'sequencer': {
        '*HODTi': HODTi,
        '*HODTf': HODTf,
        '*VODTi': VODTi,
        '*VODTm': VODTm,
        '*VODTf': VODTf,
        '*T_bm': T_bm,
        'sequence': sequence,
   },
}

if 'anti_polarize' in sequence:
    parameter_values['sequencer'].update({'*ZCCclk': -9.})


cxn = labrad.connect()
c = cxn.conductor
c.set_parameter_values(json.dumps(parameter_values))
