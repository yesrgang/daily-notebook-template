import numpy  as np
from scipy.optimize import curve_fit

def fit(function, p_dict, x, y, y_err=None, p_fix=[]):
    """ make scipy.curve_fit easier to use 
    
    Args:
        function: function to be fit. 
            pass function parameters to first call. 
            pass variable to second call.
            e.g. 
            def linear(p):
                return lambda x: p['a'] * x + p['b']
        p_dict: dictionary mapping parameter names to values.
            e.g.
            p = {'a': 1e-2, 'b': 0}
        x: array of independent data
        y: array of dependent data
        y_err: array of errorbars for y
        p_fix: list of parameter names. 
            all other parameters will be optimized by curve_fit.
    Returns:
        solutions: dictionary mapping parameter names to optimized values.
        errors: dictionary mapping parameter names to std errors of fit.
    """
    p_dict = p_dict.copy()

    fit_these = [p for p in p_dict if p not in p_fix]
    def f(x, *pfit):
        p_all = p_dict.copy()
        p_all.update({p: v for p, v in zip(sorted(fit_these), pfit)})
        return function(p_all)(x)

    pfit = [v for (p, v) in sorted(p_dict.items()) if p in fit_these]
    if y_err is not None:
        popt, pcov = curve_fit(f, x, y, pfit, sigma=y_err, absolute_sigma=True)
    else:
        popt, pcov = curve_fit(f, x, y, pfit, sigma=y_err, absolute_sigma=False)
    perr = np.sqrt(np.diag(pcov))

    solutions = p_dict
    solutions.update({p: v for p, v in zip(sorted(fit_these), popt)})
    errors = {p: 0 for p in p_dict.keys()}
    errors.update({p: v for p, v in zip(sorted(fit_these), perr)})
    
    return solutions, errors




def fit_fig(fig, func, p_guess={}, p_fix=[], fit_range=[0, None], do_print=0, show_guess=0, fig_choice=0, color='r'):
    p_guessed = p_guess.copy()
    try:
        ax = fig.get_axes()[fig_choice]
        indi, indf = fit_range
        x, y = ax.get_lines()[-1].get_xydata()[indi:indf].T
        p_fit, p_err = fit(func, p_guess, x, y, p_fix=p_fix)
        x_fit = np.linspace(x.min(), x.max(), 1000)
        if show_guess:
            raise Exception
        ax.plot(x_fit, func(p_fit)(x_fit),color)
        
        # make fit values easier to read
        p_fit = {k: v
            for k, v in p_fit.items()}
        p_err = {k: v for k, v in p_err.items()}
        if do_print:
            print '-------- fit results --------' 
            print 'fit: ', p_fit
            print 'err: ', p_err
        return p_fit, p_err
    except RuntimeError:
        print 'bad fit'
        x_fit = np.linspace(x.min(), x.max(), 1000)
        ax.plot(x_fit, func(p_guessed)(x_fit), 'r--')
        return p_guessed, p_guessed
    except Exception as e:
        print e
        x_fit = np.linspace(x.min(), x.max(), 1000)
        ax.plot(x_fit, func(p_guessed)(x_fit), 'r--')
        return p_guessed, p_guessed

""" 
fit functions
"""
def exponential(p):
    return lambda x: p['b'] + p['a'] * np.exp(-x / p['tau'])

def lorentzian(p):
    return lambda f: p['a'] / (1.0 + (2.0 * (f - p['x0']) / p['Gamma'])**2) + p['b']

def linear(p):
    return lambda x: p['a'] * x + p['b']

def sine(p):
    a = p.get('a', 1)
    b = p.get('b', 0)
    f = p.get('f', 1)
    phi = p.get('phi', 0)
    return lambda t: a * np.sin(2 * np.pi * f * t + phi) + b

    
def sin2(p):
    return lambda y: p['a'] * np.sin(np.pi * y / p['c'] + p['phi']) + p['b']
    
