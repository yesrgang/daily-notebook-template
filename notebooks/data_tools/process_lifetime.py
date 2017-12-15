import numpy as np
import matplotlib.pyplot as plt

from data_tools.fit import *
from data_tools.process_lattice_depths import process_lattice_depths
from data_tools.process_pmt import process_pmt

def process_lifetime(data, depth_coefficients):
    """
    calculate lattice depths    
    match fluorescense measurements with clock detunings.
    """
    data = process_lattice_depths(data, depth_coefficients)
    data = process_pmt(data)
    
    data['sequencer']['*T_hold_lat'] = data['sequencer']['*T_hold_lat'][:-1]

    return data

def fit_lifetime(data, fit_settings):
    data['fit_lifetime'] = {}
    for state, settings in fit_settings.items():
        p = settings.get('p')
        p_fix = settings.get('p_fix', [])
        func = settings.get('func', 'exponential')
        func = globals()[func]
        x = data['sequencer']['*T_hold_lat']
        y = data['pmt'][state]
        p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)
        data['fit_lifetime'][state] = {
            'fit': p_fit,
            'err': p_err,
        }
            
    return data

def plot_lifetime(data, fig=None, units='s'):
    times = data['sequencer']['*T_hold_lat']
    fit_times = np.linspace(min(times), max(times), 1e3)
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(4,1)
        fig.set_size_inches(8, 12)
        
    for i, state in enumerate(['frac', 'gnd', 'exc', 'tot']):
        data_line = ax[i].plot(times, data['pmt'][state], 'o')
        fitted = data.data.get('fit_lifetime')
        if fitted:
            color = data_line[0].get_color()
            ax[i].plot(fit_times, exponential(fitted[state]['fit'])(fit_times), color)
            
        ax[i].set_ylabel(state + ' [arb]')
        ax[i].set_xlabel('hold time [{}]'.format(units))
        ax[i].set_ylim([0, data['pmt'][state].max()*1.2])            
    
    plt.tight_layout()
    return fig
