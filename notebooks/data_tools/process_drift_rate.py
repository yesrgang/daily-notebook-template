import labrad
import matplotlib.pyplot as plt
import numpy as np

from data import Data
from fit import fit
from process_clock_scan import *
from process_camera import *

def get_drift_rate(center_frequency, data_sets, do_plot=True, units='Hz'):
    fig = None
    data_ = []
    ans_ = []
    err_ = []
    for data_set in data_sets:
        data = Data(data_set['filename'], data_set.get('cuts'))
        data = process_clock_scan(data, center_frequency)
        data = fit_clock_scan(data, data_set['fit_clock_scan'])
        fig = plot_clock_scan(data, fig, units='kHz')
        data_.append(data)
        ans_.append(data['fit_clock_scan']['fit'])
        err_.append(data['fit_clock_scan']['err'])

    f0_ = [center_frequency - ans['x0'] for ans in ans_]
    if err_:
        f0err_ = [err['x0'] for err in err_]
    else:
        f0err_ = None
    T_ = [data['time']['timestamp'][np.argmin(abs(data['clock_aom']['frequency']-f0))]
            for data, f0 in zip(data_, f0_)]
    T_ = [T-T_[0] for T in T_]
    
    p_guess = {'a': (f0_[-1] - f0_[0]) / T_[-1], 'b': f0_[0]}
    ans, err = fit(linear, p_guess, T_, f0_, y_err=f0err_)
    print 'drift rate: {} {}/s'.format(ans['a'], units)
    print 'error bar: {} {}/s'.format(err['a'],units)
    cxn = labrad.connect()
    cxn.rf.select_device('clock_dedrift')
    rr = cxn.rf.ramprate()
    print 'new ramprate: {} Hz/s'.format(rr + ans['a'])
    if do_plot:
        T_fit_ = np.linspace(min(T_), max(T_), 1000)
        f0_fit_ = linear(ans)(T_fit_)
        
        fig = plt.figure()
        fig.set_size_inches(8, 5)
        ax = fig.add_subplot(111)
            
        if f0err_:
            ax.errorbar(T_, f0_, f0err_, fmt='o')
        else:
            ax.plot(T_, f0_, 'o')
        ax.plot(T_fit_, f0_fit_, '-')
        ax.set_title('measure drift')
        ax.set_ylabel('center frequency [{}]'.format(units))
        ax.set_xlabel('time [s]')
        
        max_y = max([max(l.get_ydata()) for l in ax.get_lines()])
        min_y = min([min(l.get_ydata()) for l in ax.get_lines()])
        range_y = max_y - min_y
        ax.set_ylim([min_y-.1*range_y, max_y+.1*range_y])
        
        max_x = max([max(l.get_xdata()) for l in ax.get_lines()])
        min_x = min([min(l.get_xdata()) for l in ax.get_lines()])
        range_x = max_x - min_x
        ax.set_xlim([min_x-.1*range_x, max_x+.1*range_x])
        
        return fig

def get_drift_rate_camera(center_frequency, data_sets, do_plot=True, units='Hz'):
    fig = None
    data_ = []
    ans_ = []
    err_ = []
    for filename, data_set in data_sets.items():
        data = Data(filename)
        fit_settings = data_set['fit_settings']
        data['name'] = filename
        load_images(data, data_set['camera_args'])
        process_images_eg(data, data_set['camera_args'])
        data = process_clock_scan_camera(data, center_frequency)
        data = fit_clock_scan_camera(data, fit_settings)
        data_set['data'] = data
        fig = plot_clock_scan_camera(data, fit_settings['region'], fig=fig)
        data_.append(data)
        ans_.append(data['fit_clock_scan']['fit'])
        err_.append(data['fit_clock_scan']['err'])       

    f0_ = [center_frequency - ans['x0'] for ans in ans_]
    if err_:
        f0err_ = [err['x0'] for err in err_]
    else:
        f0err_ = None
    T_ = [data['time']['timestamp'][np.argmin(abs(data['clock_aom']['frequency']-f0))]
            for data, f0 in zip(data_, f0_)]
    T_ = [T-T_[0] for T in T_]
    
    p_guess = {'a': (f0_[-1] - f0_[0]) / T_[-1], 'b': f0_[0]}
    ans, err = fit(linear, p_guess, T_, f0_, y_err=f0err_)
    print 'drift rate: {} {}/s'.format(ans['a'], units)
    print 'error bar: {} {}/s'.format(err['a'],units)
    cxn = labrad.connect()
    cxn.rf.select_device('clock_dedrift')
    rr = cxn.rf.ramprate()
    print 'new ramprate: {} Hz/s'.format(rr + ans['a'])
    if do_plot:
        T_fit_ = np.linspace(min(T_), max(T_), 1000)
        f0_fit_ = linear(ans)(T_fit_)
        
        fig = plt.figure()
        fig.set_size_inches(8, 5)
        ax = fig.add_subplot(111)
            
        if f0err_:
            ax.errorbar(T_, f0_, f0err_, fmt='o')
        else:
            ax.plot(T_, f0_, 'o')
        ax.plot(T_fit_, f0_fit_, '-')
        ax.set_title('measure drift')
        ax.set_ylabel('center frequency [{}]'.format(units))
        ax.set_xlabel('time [s]')
        
        max_y = max([max(l.get_ydata()) for l in ax.get_lines()])
        min_y = min([min(l.get_ydata()) for l in ax.get_lines()])
        range_y = max_y - min_y
        ax.set_ylim([min_y-.1*range_y, max_y+.1*range_y])
        
        max_x = max([max(l.get_xdata()) for l in ax.get_lines()])
        min_x = min([min(l.get_xdata()) for l in ax.get_lines()])
        range_x = max_x - min_x
        ax.set_xlim([min_x-.1*range_x, max_x+.1*range_x])
        
        return fig