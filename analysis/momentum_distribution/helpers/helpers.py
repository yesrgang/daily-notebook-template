import numpy as np
import polylog

def TFermi(N, fbar):
    return (6. * N)**(1./3.) * fbar * hOverK

def thermal((x, y), x0, y0, sigx, sigy, background, peak):
    return background + peak*np.exp( - 0.5*( (x-x0)/(sigx) )**2 - 0.5*( (y-y0)/(sigy) )**2 )
    
def thermalfit(xy, x0, y0, sigx, sigy, background, peak):
    return thermal(xy, x0, y0, sigx, sigy, background, peak).ravel()
    
def polylog_fit((x, y), x0, y0, Rx, Ry, background, peak, q):
    return background + peak*polylog.dilog(-np.exp(q - 0.5*( (x.ravel()-x0)/Rx )**2 - 0.5*( (y.ravel()-y0)/Ry )**2 ) )


