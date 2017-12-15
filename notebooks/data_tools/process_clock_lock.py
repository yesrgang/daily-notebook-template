from data_tools.data import *
import matplotlib.pyplot as plt
import allantools
from scipy import signal

def most_recent(filename):
    if not '#' in filename:
        i = 0
        while os.path.isfile(filename+'#'+str(i)):
            i += 1
        return filename+'#'+str(i-1)
    else:
        return filename
    
def autocorrelate(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size/2:]    

def plot_clock_lock(data_filename, center_freq, units='Hz', allan_cuts=[(0, None)]):
    data = Data(most_recent(data_filename), cuts=allan_cuts)
    
    fig, ax = plt.subplots(3, 2)
    fig.set_size_inches(14, 15)
    
    ax[0,0].get_shared_x_axes().join(ax[0,0], ax[1,0])
    for i, (frac, tot, lock) in enumerate(zip(
            data['andor']['frac'][2:], 
            data['andor']['tot'][2:], 
            data['clock_servo']['dither_lock'][:-2]
            )):
        if lock['dither'][0] == '-9/2':
            ax[0,0].plot(i, frac, 'bo')
            ax[1,0].plot(i, tot, 'bo')
        else:
            ax[0,0].plot(i, frac, 'ro')
            ax[1,0].plot(i, tot, 'ro')    
    for i, (frac, tot, lock) in enumerate(zip(
            data['andor']['frac'][2:], 
            data['andor']['tot'][2:], 
            data['clock_servo']['dither_lock'][:-2]
            )):
        if (lock['dither'][0] == '-9/2') and (lock['dither'][1] == 'right'):
            f = data['andor']['frac']
            ax[0,0].plot([i, i - 2], [f[i+2], f[i]], 'b')
        if (lock['dither'][0] == '+9/2') and (lock['dither'][1] == 'right'):
            f = data['andor']['frac']
            ax[0,0].plot([i, i - 2], [f[i+2], f[i]], 'r')
    ax[0,0].set_ylim([0, 1])
    ax[0,0].set_xlabel('Experiment index')
    ax[0,0].set_ylabel('Excitation fraction')
#        else:
#            ax[0,0].plot(i, frac, 'ro')
            
    zeeman_shifts = (data['-9/2']['frequency'][4::4] - data['+9/2']['frequency'][4::4]) / 2.
    zeeman_shift = np.mean(zeeman_shifts)
    mean_freqs = (data['+9/2']['frequency'][4::4] + data['-9/2']['frequency'][4::4]) / 2.
    
    ax[0,1].plot(center_freq - mean_freqs, 'k')
    ax[0,1].plot(center_freq - data['-9/2']['frequency'][4::4] + zeeman_shift, 'b')
    ax[0,1].plot(center_freq - data['+9/2']['frequency'][4::4] - zeeman_shift, 'r')
    ax[0,1].set_ylabel('frequency [Hz]')
    ax[0,1].set_xlabel('Cycle index')
    
    freqs = mean_freqs
#    freqs = zeeman_shifts
#    freqs = np.concatenate([freqs[i:f] for i,f in allan_cuts])
    (taus, devs, errs, n) = allantools.adev(signal.detrend(freqs) / 429e12, 
            rate=1. / (4 * 14.58), data_type='freq', taus='all')
    devs_ctrl = devs
    for tau, dev, err in zip(taus, devs, errs):
        ax[1,1].plot(tau, dev, 'ko')
        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'k-')
    ax[1,1].set_yscale('log')
    ax[1,1].set_xscale('log')
    ax[1,1].set_ylabel('Instability')
    ax[1,1].set_xlabel('Averaging time')
    
   
    errp = []
    errm = []
    for i, (frac, lock) in enumerate(zip(data['andor']['frac'][2:], data['clock_servo']['dither_lock'][:-2])):
        if lock['dither'] == ['-9/2', 'right']:
            error = data['andor']['frac'][i - 2 + 2] - frac
            ax[2,0].plot(i, error, 'bo')
            errm.append(error)
        elif lock['dither'] == ['+9/2', 'right']:
            error = data['andor']['frac'][i - 2 + 2] - frac
            ax[2,0].plot(i, error, 'ro')
            errp.append(error)
    ax[2,0].set_ylim([-1, 1])
   
    
    
  
    contrast = .9
    if 'ramsey_clock' in data['sequencer']['sequence'][0]:
        print 'detected Ramsey sequence'
        err_correction_factor = contrast * .32 * .5 / np.mean(data['sequencer']['*Tramsey'])
    else:
        print 'detected Rabi sequence'
        err_correction_factor = contrast * .35 * .8 / np.mean(data['sequencer']['*Trabi'])
    
    fm_err = np.array(errm) * err_correction_factor
    
    (taus, devs, errs, n) = allantools.adev(signal.detrend(fm_err) / 429e12, 
            rate=1. / (4 * 14.58), data_type='freq', taus='all')
    devs_m = devs
    for tau, dev, err in zip(taus, devs, errs):
        ax[1,1].plot(tau, dev, 'bo')
        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'b-')   
    
    fm_uncorrected = data['-9/2']['frequency'][4::4]
    fm_corrected = fm_err[:len(fm_uncorrected)][1:] + fm_uncorrected[:len(fm_err)][:-1]
    ax[0,1].plot(range(1, len(fm_corrected)+1), center_freq - fm_corrected + zeeman_shift, 'b--')
    

    (taus, devs, errs, n) = allantools.adev(signal.detrend(fm_corrected) / 429e12, 
            rate=1. / (4 * 14.58), data_type='freq', taus='all')
    devs_m = devs
#    for tau, dev, err in zip(taus, devs, errs):
#        ax[1,1].plot(tau, dev, 'bo')
#        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'b-')   
    
    fp_err = np.array(errp) * err_correction_factor
    (taus, devs, errs, n) = allantools.adev(signal.detrend(fp_err) / 429e12, 
            rate=1. / (4 * 14.58), data_type='freq', taus='all')
    devs_p = devs
    for tau, dev, err in zip(taus, devs, errs):
        ax[1,1].plot(tau, dev, 'ro')
        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'r-')   
        
    fp_uncorrected = data['+9/2']['frequency'][4::4]
    fp_corrected = fp_err[:len(fp_uncorrected)][1:] + fp_uncorrected[:len(fp_err)][:-1]
    ax[0,1].plot(range(1, len(fp_corrected)+1), center_freq - fp_corrected - zeeman_shift, 'r--')

    (taus, devs, errs, n) = allantools.adev(signal.detrend(fp_corrected) / 429e12, 
            rate=1. / (4 * 14.58), data_type='freq', taus='all')
#    for tau, dev, err in zip(taus, devs, errs):
#        ax[1,1].plot(tau, dev, 'ro')
#        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'r-')   
        
    for tau, dc, dp, dm in zip(taus, devs_ctrl, devs_p, devs_m):
        d_tot = np.sqrt(dc**2 + (dp + dm)**2 / 4)
        ax[1,1].plot(tau, d_tot, 'o', color='magenta')
#        ax[1,1].plot([tau, tau], [dev - err, dev + err], 'r-')   

    
#    ax[2,1].plot(autocorrelate(signal.detrend(fm_uncorrected)), 'bo')
#    ax[2,1].plot(autocorrelate(signal.detrend(fm_corrected)), 'bo--')
#    ax[2,1].plot(autocorrelate(signal.detrend(fp_uncorrected)), 'ro')
#    ax[2,1].plot(autocorrelate(signal.detrend(fp_corrected)), 'ro--')
    ax[2,1].plot(autocorrelate(errm), 'bo-')
    ax[2,1].plot(autocorrelate(errp), 'ro-')

#    ax[2,1].plot(zeeman_shifts - zeeman_shift, 'k')
#    ax[2,1].set_title('zeeman shift: {}'.format(zeeman_shift))
#    ax[2,1].set_xlabel('Cycle index')
#    ax[2,1].set_ylabel('frequency (Hz)')
 
    
    return fig, ax