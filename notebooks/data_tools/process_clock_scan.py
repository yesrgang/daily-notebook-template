import numpy as np
import matplotlib.pyplot as plt
from data_tools.plot import *
from data_tools.fit import *
from data_tools.units import *
from data_tools.process_pmt import process_pmt

def process_clock_scan(data, center_freq, fig=None, plot_live=0, units='Hz'):
    """ shift pmt data and populate 'clock_aom' 'detuning' """
    data = process_pmt(data)    
    data['clock_aom']['detuning'] = -1*(data['clock_aom']['frequency'][:-1] - center_freq)
    
    return data

def fit_clock_scan(data, settings, do_print=False):
    if settings is None:
        return data
    
    p = settings.get('p')
    p_fix = settings.get('p_fix', [])
    func = settings.get('func', 'lorentzian')
    state = settings.get('state', 'frac')
    det = data['clock_aom']['detuning']
    xlim = settings.get('xlim', [min(det), max(det)])
    func = globals()[func]
    in_range = np.where(np.logical_and(det>xlim[0], det<xlim[1]))
    x = data['clock_aom']['detuning'][in_range]
    y = data['pmt'][state][in_range]
    p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)

    data['fit_clock_scan'] = {
        'xlim': xlim,
        'func': func,
        'state': state,
        'fit': p_fit,
        'err': p_err,
    }
            
    return data    

def plot_clock_scan(data, fig, units='Hz'):
    order = np.argsort(data['clock_aom']['detuning'])
    freqs = data['clock_aom']['detuning'][order] / unit_factor[units]
    fracs = data['pmt']['frac'][order]
    tots = data['pmt']['tot'][order]
    excs = data['pmt']['exc'][order]
    
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(2, 1)
        fig.set_size_inches(8, 12)
    
    frac_ln, = ax[0].plot(freqs, fracs)
    ax[0].set_title('clock scan $|e\\rangle$')
    ax[0].set_ylabel('excitation fraction')
    ax[0].set_xlabel('clock aom frequency ({})'.format(units))
    
    tot_ln, = ax[1].plot(freqs, tots)
    exc_ln, = ax[1].plot(freqs, excs)

    ax[1].set_title('atom number')
    ax[1].set_ylabel('atom number (arb.)')
    ax[1].set_xlabel('clock aom frequency ({})'.format(units))
    ax[1].legend(['total', 'excited'], loc='best')
    
    fitted = data.data.get('fit_clock_scan')
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
                
    return fig
