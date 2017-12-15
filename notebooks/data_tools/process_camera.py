import h5py
import numpy as np
import matplotlib.pyplot as plt
import mahotas
from data_tools.units import *
from data_tools.fit import *

DATA_DIRECTORY = '/home/srgang/yesrdata/SrQ/data/{}/'

def load_images(data, settings):
    """ load images """
    camera_name = settings['name']
    off_x, off_y = settings['offset']
    width, height = settings['size']
    
    sub_px = [off_x - width / 2, off_x + width / 2, off_y - height / 2, off_y + height / 2]
    
    images = {}
    for image_path in data[camera_name]['image_path']:
        # delete try/except after 20171116
        try:            
            images_hdf5 = h5py.File('../' + image_path + '.hdf5', 'r')
        except:
            image_path = DATA_DIRECTORY.format(image_path[0]) + image_path[1]
            images_hdf5 = h5py.File(image_path, 'r')

        for key, image in images_hdf5.items():
            if not images.has_key(key):
                images[key] = []
            image = np.array(image, dtype=np.uint16)
            image = np.fliplr(np.flipud(image))
            sub_image = image[sub_px[2]:sub_px[3],sub_px[0]:sub_px[1]]
            images[key].append(sub_image)
    images = {key: np.array(value) for key, value in images.items()} 
    
    # update data object
    data[camera_name].update(images)
    
    save_images(data, images)

def save_images(data, images):
    """ save all images to single file """
    sub_images_filename = data['name'] + '-images.hdf5'
    images_hdf5 = h5py.File(sub_images_filename)
    for key, value in images.items():
        if key in images_hdf5:
            del images_hdf5[key]
        images_hdf5.create_dataset(key, data=value, compression='gzip', compression_opts=4, dtype='f')
    images_hdf5.close()    
    
def process_images_eg(data, settings):
    """ process images of e and g atoms """
    name = settings.get('name')
    pixel_size = settings.get('pixel_size', 0.55793991) # [um]
    cross_section = settings.get('cross_section', 0.1014) # [um^2]
    linewidth = settings.get('linewidth', 201.06192983) # [2 pi MHz]
    pulse_length = settings.get('pulse_length', 5) # [us]
    efficiency = settings.get('efficiency', 0.50348) 
    gain = settings.get('gain', 0.25)
    
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section
    
    # having trouble vectorizing calculation thought this could be done for speedup
    data[name]['n_g'] = []  
    data[name]['n_e'] = []
    data[name]['tot'] = []
    data[name]['frac'] = []    
    
    for i in range(len(data[name]['bright'])):
        bright = np.array(data[name]['bright'][i], dtype='f') - np.array(data[name]['dark_bright'][i], dtype='f')
        image_g = np.array(data[name]['image_g'][i], dtype='f') - np.array(data[name]['dark_g'][i], dtype='f')
        image_e = np.array(data[name]['image_e'][i], dtype='f') - np.array(data[name]['dark_e'][i], dtype='f')
    
        norm_indicies = get_norm_indicies(bright, settings['norm'])
    
        bright_g = bright * np.sum(image_g[norm_indicies]) / np.sum(bright[norm_indicies])
        image_g, bright_g = fix_image_gradient(image_g, bright_g, settings['norm'])
        
        i_g = (image_g > 0) & (bright_g > 0)
        n_g = np.zeros_like(bright)
        n_g[i_g] = (
            low_intensity_coefficient * np.log(bright_g[i_g] / image_g[i_g])
            + high_intensity_coefficient * (bright_g[i_g] - image_g[i_g])
            )
    
        bright_e = bright * np.sum(image_e[norm_indicies]) / np.sum(bright[norm_indicies])
        image_e, bright_e = fix_image_gradient(image_e, bright_e, settings['norm'])
        
        i_e = (image_e > 0) & (bright_e > 0)
        n_e = np.zeros_like(bright)
        n_e[i_e] = (
            low_intensity_coefficient * np.log(bright_e[i_e] / image_e[i_e])
            + high_intensity_coefficient * (bright_e[i_e] - image_e[i_e])
            )

        data[name]['n_g'].append(n_g)  
        data[name]['n_e'].append(n_e)
        tot = n_g + n_e
        data[name]['tot'].append(tot)
        data[name]['frac'].append(n_e / tot)
  
    
    for roi_name, roi in settings['roi'].items():
        pts = region_pts(get_roi_corners(n_g, roi))
        g_sum = np.array([np.sum(data[name]['n_g'][i][zip(*pts)]) for i in range(len(data['time']['timestamp']))])
        e_sum = np.array([np.sum(data[name]['n_e'][i][zip(*pts)]) for i in range(len(data['time']['timestamp']))])
        
        data[roi_name] = {
            'n_g': g_sum,
            'n_e': e_sum,
            'frac': e_sum / (e_sum + g_sum),
            'tot': e_sum + g_sum,
            }
        
    save_images(data, {'n_g': n_g, 'n_e': n_e})    
    
def process_images_g(data, settings):
    """ process images of g atoms """
    name = settings.get('name')
    pixel_size = settings.get('pixel_size', 0.55793991) # [um]
    cross_section = settings.get('cross_section', 0.1014) # [um^2]
    linewidth = settings.get('linewidth', 201.06192983) # [2 pi MHz]
    pulse_length = settings.get('pulse_length', 5) # [us]
    efficiency = settings.get('efficiency', 0.50348) 
    gain = settings.get('gain', 0.25)
  
    
    high_intensity_coefficient = 2 / (linewidth * pulse_length * efficiency * gain)
    low_intensity_coefficient = pixel_size**2 / cross_section
    
    """"""
    # having trouble vectorizing calculation thought this could be done for speedup
    data[name]['n'] = []  
    
    for i in range(len(data[name]['bright'])):
        bright = np.array(data[name]['bright'][i], dtype='f') - np.array(data[name]['dark'][i], dtype='f')
        image = np.array(data[name]['image'][i], dtype='f') #- np.array(data[name]['dark'][i], dtype='f')
    
        norm_indicies = get_norm_indicies(bright, settings['norm'])
    

        bright = bright * np.sum(image[norm_indicies]) / np.sum(bright[norm_indicies])
        image, bright = fix_image_gradient(image, bright, settings['norm'])
        
        n = (
            low_intensity_coefficient * np.clip(np.log(bright / image), 0, None)
            + high_intensity_coefficient * (bright - image)
            )

        data[name]['n'].append(n)  

    for roi_name, roi in settings['roi'].items():
        pts = region_pts(get_roi_corners(n, roi))
        data[roi_name] = {
            'n': [np.sum(data[name]['n'][i][zip(*pts)]) for i in range(len(data[name]['bright']))]
            }
        
    
    save_images(data, {'n': n})
    
def fix_image_gradient(image1, image2, norm):
    x_max = image1.shape[-1]
    y_max = image1.shape[-2]
    x, y = np.meshgrid(range(x_max), range(y_max))    

    norm_indicies = get_norm_indicies(image1, norm)
    x0 = np.mean(x[norm_indicies])
    y0 = np.mean(y[norm_indicies])
    x2 = np.mean(x[norm_indicies] * (x[norm_indicies] - x0))
    y2 = np.mean(y[norm_indicies] * (y[norm_indicies] - y0))
    
    m_x = np.mean((x[norm_indicies] - 0 * x0) * (image1[norm_indicies] - image2[norm_indicies])) / x2
    m_y = np.mean((y[norm_indicies] - 0 * y0) * (image1[norm_indicies] - image2[norm_indicies])) / y2
                       
    correction = m_x * (x - x0) + m_y * (y - y0)
    return image1, image2 + correction

def get_norm_indicies(image, norm):
    x_max = image.shape[-1]
    y_max = image.shape[-2]
    x, y = np.meshgrid(range(x_max), range(y_max))    
    r2 = (x - x_max / 2.)**2 + (y - y_max / 2.)**2
    return (r2 > norm[2]**2) & (r2 < norm[3]**2)

def get_roi_corners(image, roi, theta=0):
    x_max = image.shape[-1]
    y_max = image.shape[-2]
    
    R = np.matrix([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    h, w, x0, y0 = roi
    corners = [
        np.array([x0-w, y0-h]), 
        np.array([x0-w, y0+h]), 
        np.array([x0+w, y0+h]), 
        np.array([x0+w, y0-h]),
        ]
    for i, pt in enumerate(corners):
        corners[i] = np.dot(pt, R.T).astype('int').tolist()[0]
    
    return corners + np.array([x_max, y_max]) / 2.

def region_pts(pts):
    x_pts, y_pts = zip (*pts)
    x_min, x_max = np.min(x_pts), np.max(x_pts)
    y_min, y_max = np.min(y_pts), np.max(y_pts)

    new_pts = [(int(x - x_min), int(y - y_min)) for x, y in pts]

    X = x_max - x_min + 1
    Y = y_max - y_min + 1
    grid = np.zeros((X.astype(np.int_), Y.astype(np.int_)))
    mahotas.polygon.fill_polygon(new_pts, grid)
    return [(int(x + x_min), int(y + y_min)) for (x, y) in zip(*np.nonzero(grid))]
    
def plot_camera_image(image, settings, cmap='inferno', vmin=None, vmax=None):
    """ plot images """
    fig, ax = plt.subplots(1)
    ax.pcolormesh(image, cmap=cmap, vmin=vmin, vmax=vmax)

    
    norm_indicies = get_norm_indicies(image, settings['norm'])
    ax.contour(norm_indicies, colors='red', linewidths=2)
    
    for roi in settings['roi'].values():
        corners = get_roi_corners(image, roi)
        x, y = zip(*corners)
        x = list(x) + [x[0]]
        y = list(y) + [y[0]]
        
        ax.plot(x, y, color='w', linewidth=2, alpha=1)
    x_max = image.shape[1]
    y_max = image.shape[0]
    
    pixel_size = 0.55793991 # [um]
    x_tick_step = 20
    y_tick_step = 20
    ix_max = x_max / x_tick_step / 4    
    iy_max = y_max / y_tick_step / 4
    
    xticks = [x_tick_step / pixel_size * i + x_max / 2. for i in range(-ix_max, ix_max + 1)]
    yticks = [y_tick_step / pixel_size * i + x_max / 2. for i in range(-iy_max, iy_max + 1)]
    xticklabels = [x_tick_step * i for i in range(-ix_max, ix_max + 1)]
    yticklabels = [y_tick_step * i for i in range(-iy_max, iy_max + 1)]
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xticklabels(xticklabels)
    ax.set_yticklabels(yticklabels)
    
    ax.set_xlabel(r'$x$ ($\mu\mathrm{m}$)')
    ax.set_ylabel(r'$y$ ($\mu\mathrm{m}$)')

    ax.set_aspect('equal')
                
    return fig, ax


def process_clock_scan_camera(data, center_freq, fig=None, plot_live=0, units='Hz'):
    """ shift pmt data and populate 'clock_aom' 'detuning' """
    data['clock_aom']['detuning'] = -1*(data['clock_aom']['frequency'] - center_freq) 
    return data

def plot_clock_scan_camera(data, region, fig=None, units='Hz'):
    order = np.argsort(data['clock_aom']['detuning'])
    freqs = data['clock_aom']['detuning'][order] / unit_factor[units]
    fracs = data[region]['frac'][order]
    tots = data[region]['tot'][order]
    excs = data[region]['n_e'][order]
    gnds = data[region]['n_g'][order]
    
    
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
    gnd_ln, = ax[1].plot(freqs, gnds)
    

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

def plot_rabi_flop_camera(data, region, fig, units='s'):
    order = np.argsort(data['sequencer']['*Trabi'])
    times = data['sequencer']['*Trabi'][order] / unit_factor[units]
    fracs = data[region]['frac'][order]
    tots = data[region]['tot'][order]
    excs = data[region]['n_e'][order]
    
    
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



def plot_bias_scan_camera(data, region, direction, fig=None):
    order = np.argsort(data['sequencer'][direction])
    fields = data['sequencer'][direction][order]
    fracs = data[region]['frac'][order]
    tots = data[region]['tot'][order]
    excs = data[region]['n_e'][order]
    gnds = data[region]['n_g'][order]
    
    if fig:
        ax = fig.get_axes()
    else:
        fig, ax = plt.subplots(2, 1)
        fig.set_size_inches(8, 12)
    
    frac_ln, = ax[0].plot(fields, fracs)
    ax[0].set_title('clock scan $|e\\rangle$')
    ax[0].set_ylabel('excitation fraction')
    ax[0].set_xlabel('{} voltage'.format(direction))
    
    
    tot_ln, = ax[1].plot(fields, tots)
    exc_ln, = ax[1].plot(fields, excs)
    gnd_ln, = ax[1].plot(fields, gnds)
    

    ax[1].set_title('atom number')
    ax[1].set_ylabel('atom number (arb.)')
    ax[1].set_xlabel('{} voltage'.format(direction))
    ax[1].legend(['total', 'excited'], loc='best')
    
    fitted = data.data.get('fit_bias_scan')
    if fitted:
        d = fitted
        fit_freqs = np.linspace(d['xlim'][0], d['xlim'][1], 1e3)
        fit_freqs_plt = fit_freqs
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

def fit_clock_scan_camera(data, settings=None, do_print=False):
    if settings is None:
        return data
    
    p = settings.get('p')
    p_fix = settings.get('p_fix', [])
    func = settings.get('func', 'lorentzian')
    state = settings.get('state', 'frac')
    region = settings.get('region')
    det = data['clock_aom']['detuning']
    xlim = settings.get('xlim', [min(det), max(det)])
    func = globals()[func]
    in_range = np.where(np.logical_and(det>xlim[0], det<xlim[1]))
    x = data['clock_aom']['detuning'][in_range]
    y = data[region][state][in_range]
    p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)
    if do_print:
        print 'fit: ', p_fit
        print 'err: ', p_err

    data['fit_clock_scan'] = {
        'xlim': xlim,
        'func': func,
        'state': state,
        'fit': p_fit,
        'err': p_err,
    }
            
    return data 



def fit_rabi_flop_camera(data, settings=None, do_print=False):
    if settings is None:
        return data

    p = settings.get('p')
    p_fix = settings.get('p_fix', [])
    func = settings.get('func', 'sin2')
    state = settings.get('state', 'frac')
    region = settings.get('region')
    
    times = data['sequencer']['*Trabi']
    xlim = settings.get('xlim', [min(times), max(times)])
    func = globals()[func]
    in_range = np.where(np.logical_and(times>xlim[0], times<xlim[1]))
    x = times[in_range]
    y = data[region][state][in_range]
    
    p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)
    if do_print:
        print 'fit: ', p_fit
        print 'err: ', p_err    

    data['fit_rabi_flop'] = {
        'xlim': xlim,
        'func': func,
        'state': state,
        'fit': p_fit,
        'err': p_err,
    }
            
    return data    
