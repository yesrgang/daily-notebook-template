import numpy as np
import matplotlib.pyplot as plt

from plot import *
from fit import *
from units import *
from process_pmt import process_pmt

def process_rabi_flop(data):
    """ shift pmt data """
    data = process_pmt(data)    
    data['sequencer']['*Trabi'] = data['sequencer']['*Trabi'][:-1]
    
    return data

def fit_rabi_flop(data, settings):
    if settings is None:
        return data
    
    p = settings.get('p')
    p_fix = settings.get('p_fix', [])
    func = settings.get('func', 'sine')
    state = settings.get('state', 'frac')
    times = data['sequencer']['*Trabi']
    xlim = settings.get('xlim', [min(times), max(times)])
    func = globals()[func]
    in_range = np.where(np.logical_and(times>xlim[0], times<xlim[1]))
    x = times[in_range]
    y = data['pmt'][state][in_range]
    p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)

    data['fit_rabi_flop'] = {
        'xlim': xlim,
        'func': func,
        'state': state,
        'fit': p_fit,
        'err': p_err,
    }
            
    return data    

def plot_rabi_flop(data, fig, units='Hz'):
    order = np.argsort(data['sequencer']['*Trabi'])
    times = data['sequencer']['*Trabi'][order] / unit_factor[units]
    fracs = data['pmt']['frac'][order]
    tots = data['pmt']['tot'][order]
    excs = data['pmt']['exc'][order]
    
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(2, 1)
        fig.set_size_inches(8, 12)
    
    frac_ln, = ax[0].plot(times, fracs, 'o-')
    ax[0].set_title('rabi flop')
    ax[0].set_ylabel('excitation fraction')
    ax[0].set_xlabel('pulse duration ({})'.format(units))
    
    tot_ln, = ax[1].plot(times, tots)
    exc_ln, = ax[1].plot(times, excs)

    ax[1].set_title('atom number')
    ax[1].set_ylabel('atom number (arb.)')
    ax[1].set_xlabel('pulse duration ({})'.format(units))
    ax[1].legend(['total', 'excited'], loc='best')
    
    fitted = data.data.get('fit_rabi_flop')
    if fitted:
        d = fitted
        fit_freqs = np.linspace(d['xlim'][0], d['xlim'][1], 1e3)
        fit_freqs_plt = fit_freqs / unit_factor[units]
        if d['state'] == 'frac':
            color = frac_ln.get_color()
            ax[0].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), color)
            ax[0].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), 'r-')
        elif d['state'] == 'tot':
            color = tot_ln.get_color()
            ax[1].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), color)  
            ax[1].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), 'r-')
        elif d['state'] == 'exc':
            color = exc_ln.get_color()
            ax[1].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), color)  
            ax[1].plot(fit_freqs_plt, d['func'](d['fit'])(fit_freqs), 'r-')                 
                
    return fig, ax
