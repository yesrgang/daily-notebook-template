from data_tools.fit import *

def process_odt_slosh(data, camera='Mako2'):
    data = process_camera(data, camera)
    
    data['sequencer']['*Tslosh'] = data['sequencer']['*Tslosh'][:-1] 
    
def fit_odt_slosh(data, fit_settings):
    times = data['sequencer']['*Tslosh']
    
    p = settings.get('p')
    p_fix = settings.get('p_fix', [])
    func = settings.get('func', 'sin')
    func = globals()[func]
    axis = settings.get('axis', 'y')
    camera = settings.get('camera', 'Mako2')
    xlim = settings.get('xlim', [min(times), max(times)])
    in_range = np.where(np.logical_and(times>xlim[0], times<xlim[1]))
    x = times[in_range]
    y = data[camera][axis][in_range]
    p_fit, p_err = fit(func, p, x, y, p_fix=p_fix)
    data['fit_odt_slosh'] = {
        'xlim': xlim,
        'func': func,
        'axis': state,
        'fit': p_fit,
        'err': p_err,
    }        
    
    return data
    
def plot_odt_slosh(data, fig, camera='Mako2', axis='y', units='ms'):
    times = data['sequencer']['*Tslosh'] / unit_factor[units]
    displacements = data[camera][axis]

    if fig:
        ax = fit.get_axes()[0]
    else:
        fig, ax = plt.subplots(1)
        fig.set_size_inches(8, 6)

    bx.plot(t, y0, 'o')
    bx.set_ylabel('displacement (pixels)')
    bx.set_xlabel('time ({})'.format(units))
    
    return fig
