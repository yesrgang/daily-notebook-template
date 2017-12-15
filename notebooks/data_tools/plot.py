import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

my_params = {
    #'text.usetex': True,
    'mathtext.default': 'regular',
    'font.family': 'sans-serif',
    'font.weight': 'normal',

    'axes.linewidth': 2,
    'figure.figsize': (8.0, 6.0),
    'figure.subplot.hspace': .3,
    'figure.subplot.wspace': .3,
    'font.size': 16,
    'lines.linewidth': 2,
    'xtick.minor.width': 1.5,    
    'xtick.major.width': 1.5,
    'ytick.minor.width': 1.5,    
    'ytick.major.width': 1.5,
    'xtick.minor.pad': 10,    
    'xtick.major.pad': 10,
    'ytick.minor.pad': 10,    
    'ytick.major.pad': 10,
}
mpl.rcParams.update(my_params)
    