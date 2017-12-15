"""
imports
"""

import json
import types
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import os

#sys.path.append('Z:\\SrQ\\data\\')
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_tools.data import Data
from data_tools.fit import fit
from data_tools.fit import fit2
from data_tools.units import unit_factor
from data_tools.misc import round_significant, round_from_value
from IPython import display
import time
from IPython.display import HTML
import matplotlib.dates as mdates
import scipy.special as sp

sys.path.append(os.path.join(os.path.dirname(__file__)))
from scipy import signal
from allantools import *
import clock_analyzer
reload(clock_analyzer)

my_params = {
    'axes.linewidth': 1.5,
    'figure.figsize': (8.0, 6.0),
    'figure.subplot.hspace': .3,
    'figure.subplot.wspace': .3,
    'font.size': 16,
    'lines.linewidth': 1.5,
    'xtick.minor.width': 1.5,    
    'xtick.major.width': 1.5,
    'ytick.minor.width': 1.5,    
    'ytick.major.width': 1.5,
    'xtick.minor.pad': 8,    
    'xtick.major.pad': 8,
    'ytick.minor.pad': 8,    
    'ytick.major.pad': 8,
}
mpl.rcParams.update(my_params)

"""
constants
"""
nm = 1e-9
kHz = 1e3


lamlattice = 813.4*nm
c = 299792458
hbar = 1.054571628e-34
h = hbar*2*np.pi
kb = 1.3806504e-23
amu = 1.66053873e-27
mSr = 86.9088774970*amu


"""
plotters
"""
def most_recent(filename):
    if not '#' in filename:
        i = 0
        while os.path.isfile(filename+'#'+str(i)):
            i += 1
        return filename+'#'+str(i-1)
    else:
        return filename

def plot_clock_scan(data_filename, center_freq, fig=None, plot_live=0, 
                    units='kHz'):
    data = Data(most_recent(data_filename))
#    tot = data['pico']['tot'][1:]
#    frac = data['pico']['frac'][1:]
    tot = data['pico']['tot'][1:]
    frac = data['pico']['frac'][1:]
    f_aom = -1*(data['clock_aom']['frequency'][:-1] - center_freq)/unit_factor[units]   
    order = np.argsort(f_aom)
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(1, 2)
        fig.set_size_inches(20, 8)
    
    ax[0].plot(f_aom[order], frac[order])
    ax[0].set_title(most_recent(data_filename).split('/')[-1])
    ax[0].set_ylabel('excitation fraction')
    ax[0].set_xlabel('clock aom frequency [{}]'.format(units))
    max_point = max([max(l.get_ydata()) for l in ax[0].get_lines()])
    min_point = min([min(l.get_ydata()) for l in ax[0].get_lines()])
    
    ax[0].set_ylim([min(0, 0.8*min_point), max_point*1.2])
    
    ax[1].plot(f_aom[order], tot[order])
    ax[1].set_title('atom number')
    ax[1].set_ylabel('atom number [arb.]')
    ax[1].set_xlabel('clock aom frequency [{}]'.format(units))
    ax[1].legend(['total', 'excited'], loc='best')
    ax[1].set_ylim([0, tot.max()*1.2])
    
    return fig

def plot_clock_camera(data_filename, center_freq, fig=None, plot_live=0, units='kHz'):
    data = Data(most_recent(data_filename))    
    gnd = data['Andor Ikon']['NSum1'][1:]
    exc = data['Andor Ikon']['NSum2'][1:]
    tot = gnd + exc
    frac = exc / tot
    
    f_aom = -1*(data['clock_aom']['frequency'][:-1] - center_freq)/unit_factor[units]   
    order = np.argsort(f_aom)
    
    if fig:
        ax = fig.get_axes()[0]
        bx = fig.get_axes()[1]
        #cx = fig.get_axes()[2]
    else:
        fig = plt.figure()
        fig.set_size_inches(8, 12)
        ax = fig.add_subplot(211)
        bx = fig.add_subplot(212)
        #cx = fig.add_subplot(323)
        #dx = fig.add_subplot(324)
        #ex = fig.add_subplot(325)
        #fx = fig.add_subplot(326)
        
    
    ax.plot(f_aom[order], frac[order])
    ax.set_title('clock scan')
    ax.set_ylabel('excitation fraction')
    ax.set_xlabel('clock aom frequency [{}]'.format(units))
    max_point = max([max(l.get_ydata()) for l in ax.get_lines()])
    min_point = min([min(l.get_ydata()) for l in ax.get_lines()])
    
    ax.set_ylim([min(0, 0.8*min_point), max_point*1.2])
    
    bx.plot(f_aom[order], tot[order])
    bx.set_title('atom number')
    bx.set_ylabel('atom number [arb.]')
    bx.set_xlabel('clock aom frequency [{}]'.format(units))
    bx.legend(['total', 'excited'], loc='best')
    bx.set_ylim([0, tot.max()*1.2])
    
    return fig

def plot_clock_scan_bias(data_filename, scan_field, fig=None):
    data = Data(most_recent(data_filename))
    tot = data['pico']['tot'][1:]
    frac = data['pico']['frac'][1:]
    
    biases = data['sequencer']['*{}CCclk'.format(scan_field)][:-1]
    order = np.argsort(biases)
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(2, 1)
        fig.set_size_inches(8, 12)
        
    
    ax[0].plot(biases[order], frac[order])
    ax[0].set_title('clock bias scan'.format(scan_field))
    ax[0].set_ylabel('excitation fraction')
    ax[0].set_xlabel('{} bias field [V]'.format(scan_field))
    max_point = max([max(l.get_ydata()) for l in ax[0].get_lines()])
    min_point = min([min(l.get_ydata()) for l in ax[0].get_lines()])
    
    ax[0].set_ylim([min(0, 0.8*min_point), max_point*1.2])
    
    ax[1].plot(biases[order], tot[order])
    ax[1].set_title('atom number')
    ax[1].set_ylabel('atom number [arb.]')
    ax[1].set_xlabel('{} bias field [V]'.format(scan_field))
    ax[1].legend(['total', 'excited'], loc='best')
    ax[1].set_ylim([0, tot.max()*1.2])
    
    return fig

def plot_scan_slosh(data_filename, camera='Mako2', fig=None, units='ms'):
    data = Data(most_recent(data_filename))
    x0 = data[camera]['x0'][1:]
    y0 = data[camera]['y0'][1:]
    
    t = data['sequencer']['*Tslosh'][1:]/unit_factor[units] 
    
    if fig:
        ax = fig.get_axes()[0]
        bx = fig.get_axes()[1]
        #cx = fig.get_axes()[2]
    else:
        fig = plt.figure()
        fig.set_size_inches(8, 12)
        ax = fig.add_subplot(211)
        bx = fig.add_subplot(212)
    
    ax.plot(t, x0,'ro')
    ax.set_title('slosh')
    ax.set_ylabel('x_0 (um)')
    ax.set_xlabel('time [{}]'.format(units))
    
    bx.plot(t, y0,'bo')
    bx.set_title('slosh')
    bx.set_ylabel('y_0 (um)')
    bx.set_xlabel('time [{}]'.format(units))
    
    return fig


def plot_clock_lock(data_filename, center_freq, fig=None, units='Hz', subtract=None, allan_line=None, correct_by_error=True):
    data = Data(most_recent(data_filename))
    analyzer = clock_analyzer.analyzer(data)
    analyzer.add(clock_analyzer.get_locks, f0=center_freq, allan=allan_line)
    if correct_by_error:
        analyzer.add(clock_analyzer.correct_by_error)
    if subtract != None:
        analyzer.add(clock_analyzer.self_comparison, locks=subtract)
    analyzer.analyze()
    return analyzer.plot()

def plot_clock_lock2(data_filename,
                     center_freq,
                     fig=None,
                     units='Hz',
                     average=["+9/2", "-9/2"],
                     allan_line=None,
                     correct_by_error=True,
                    subtract_first_value=True):
    data = Data(most_recent(data_filename))
    if len(data['time']['timestamp']) > 4:
        analyzer = clock_analyzer.analyzer(data)
        analyzer.add(clock_analyzer.get_locks,
                     f0=center_freq,
                     allan=allan_line,
                     subtract_first_value=subtract_first_value)
        if correct_by_error:
            analyzer.add(clock_analyzer.correct_by_error)
        if average != None:
            analyzer.add(clock_analyzer.plus_minus, locks=average)
        analyzer.add(clock_analyzer.linear_drift)
        analyzer.analyze()
        return analyzer.plot()
    else:
        return plt.figure()

def plot_rabi_flop(data_filename, fig=None, plot_live=0, units='ms'):
    data = Data(most_recent(data_filename))    
    tot = data['pico']['tot'][1:]
    frac = data['pico']['frac'][1:]
    
    #evap_param(data)
    t = data['sequencer']['*Trabi'][:-1]/unit_factor[units]
    
    if fig:
        ax = fig.get_axes()[0]
        bx = fig.get_axes()[1]
    else:
        fig = plt.figure()
        fig.set_size_inches(8, 11)
        ax = fig.add_subplot(211)
        bx = fig.add_subplot(212)
        
    ax.plot(t, frac,'o')
    ax.set_title(most_recent(data_filename).split('/')[-1])
    ax.set_ylabel('excitation fraction [arb.]')
    ax.set_xlabel('clock duration [{}]'.format(units))
    max_point = max([max(l.get_ydata()) for l in ax.get_lines()])
    min_point = min([min(l.get_ydata()) for l in ax.get_lines()])
    
    ax.set_ylim([0, max_point*1.2])
    
    
    bx.plot(t, tot)
    bx.set_title('rabi flop')
    bx.set_ylabel('total atom number [arb.]')
    bx.set_xlabel('clock duration [{}]'.format(units))
    max_point = max([max(l.get_ydata()) for l in bx.get_lines()])
    min_point = min([min(l.get_ydata()) for l in bx.get_lines()])
    bx.set_ylim([0.8*min_point, max_point*1.2])
  
    
    return fig
