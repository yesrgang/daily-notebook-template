import os
import json
import numpy as np
from scipy.io import loadmat
from scipy.optimize import curve_fit
from scipy.interpolate import spline
import matplotlib as mpl
import matplotlib.pyplot as plt

from helpers.helpers import thermal
from helpers.helpers import thermalfit
from helpers.helpers import polylog_fit
import helpers.polylog as polylog

COLORMAP = 'magma_r'

my_params = {
    'figure.figsize': (5, 4),
    'text.latex.preamble': [
        r'\usepackage{siunitx}', 
        r'\usepackage{sfmath}', 
        r'\sisetup{detect-family = true}',
        r'\usepackage{amsmath}'
    ],
    'axes.linewidth': 1,
    'xtick.major.size': 4,
    'xtick.major.width': 1,
    'xtick.minor.size': 2,
    'xtick.minor.width': 1,
    'ytick.major.size': 4,
    'ytick.major.width': 1,
    'ytick.minor.size': 2,
    'ytick.minor.width': 1,
    'font.family': 'sans-serif',
    'font.weight': 'normal',
    'font.size': 14,
}
mpl.rcParams.update(my_params)

""" image specific settings """
FILENAME = '../../evap-0.065#0.mat'


TOF = 20 # [ms]
PIXEL_RANGE = ((190, 390), (340, 580)) # ((xmin, xmax), (ymin, ymax))
P_THERMAL = [260, 406, 25, 25, 0, 1] # fit guess. [x0, y0, sigmax, sigmay, bg, peak]
R_MAX = 200 # [px] pixels in final plot
R_BIN = 2 # [px] radial averaging bin width
V_MAX = 10 # [mm/s] max velocity in final plot


""" load image """
currentfile = loadmat(FILENAME)
(xmin, xmax), (ymin, ymax) = PIXEL_RANGE
currentImage = currentfile['myN'][ymin:ymax, xmin:xmax]
pixelsize = currentfile['analysis']['pixelsize'][0][0].squeeze()
x, y = np.meshgrid(pixelsize*np.arange(0., currentImage.shape[1]),
                   pixelsize*np.arange(0., currentImage.shape[0]))

plt.imshow(currentImage)
plt.savefig('im.pdf')

""" do thermal and polylog fits """

thermal_guess = thermal((x, y), *P_THERMAL)
plt.imshow(thermal_guess)
plt.savefig('guess.pdf')

popt_thermal, pcov = curve_fit(thermalfit, (x, y), currentImage.ravel(), p0=P_THERMAL)
print 'thermal params', popt_thermal
P_POLYLOG = list(popt_thermal) + [1] # fit guess. [x0, y0, sigmax, sigmay, bg, peak, q]

fermi_guess = polylog_fit((x,y), *P_POLYLOG).reshape(x.shape)
popt_poly1, pcov_poly1 = curve_fit(polylog_fit, (x, y), currentImage.ravel(), p0=P_POLYLOG)

thermal_fit = thermal((x,y), *popt_thermal)
fermi_fit = polylog_fit((x,y), *popt_poly1).reshape(x.shape)


plt.figure(figsize=(15,5))
plt.subplot(1,4,1)
# plt.imshow(thermal_fit)
plt.imshow(thermal_guess)
plt.subplot(1,4,2)
plt.imshow(currentImage)
plt.subplot(1,4,3)
plt.imshow(currentImage - thermal_fit)

Tfit = 0.01045 * popt_thermal[3]**2 / TOF**2
Tfit_poly = 0.01045 * popt_poly1[3]**2 / TOF**2
print "temp (thermal fit): {} uK".format(Tfit)
print "temp (poly fit): {} uK".format(Tfit_poly)
print popt_poly1


# In[6]:

# Velocity data
vx = (x - popt_poly1[0])/TOF
vy = (y - popt_poly1[1])/TOF

plt.figure(figsize=(5,4))
plt.pcolor(vx, vy, currentImage/pixelsize**2,linewidth=0,rasterized=True, cmap=COLORMAP)
plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.colorbar(label='$\mathsf{\\tilde n}$ ($\mathsf{\mu m^{-2}}$)', cmap=COLORMAP)
plt.gca().set_xlabel('$\mathsf{v_x}$ (mm/s)')
plt.ylabel('$\mathsf{v_y}$ (mm/s)')
plt.gcf().subplots_adjust(bottom=0.15,left=0.16)
# plt.savefig('../tof_image.pdf')


# In[7]:

r = np.sqrt( (x - popt_thermal[0])**2 + (y - popt_thermal[1])**2 )
v = r/TOF
Ntot = np.sum(currentImage[r < R_MAX])
TTFshape = ( 6*polylog.fermi_poly3(popt_poly1[-1])[0] )**(-1./3.)
err = np.sqrt(np.diag(pcov_poly1))[-1]
print ( 6*polylog.fermi_poly3(popt_poly1[-1]-err)[0] )**(-1./3.)
print 'Atom Number: ', Ntot
print 'Fitted T/TF: ', TTFshape

# In[8]:

# MAKE PLOT, NO RESIDUALS
rVectorAll = np.arange(0., R_MAX, R_BIN*pixelsize)
rVector = (rVectorAll[:-1] + rVectorAll[1:])/2
density = np.empty_like(rVector)
density_thermal = np.empty_like(rVector)
density_zero = np.empty_like(rVector)
density_fermi = np.empty_like(rVector)
density_err = np.empty_like(rVector)

noisePerPixel = np.std(currentImage - thermal_fit)


for i, trash in enumerate(rVector):
    ind = (r > rVectorAll[i]) & (r < rVectorAll[i+1])
    density[i] = np.sum(currentImage[ind]/(pixelsize**2)) / np.sum(ind)
    density_err[i] = (noisePerPixel/(pixelsize**2)) / np.sqrt(np.sum(ind))
    density_thermal[i] = (np.sum(thermal_fit[ind])/(pixelsize**2)) / np.sum(ind)
    density_fermi[i] = (np.sum(fermi_fit[ind])/(pixelsize**2)) / np.sum(ind)    

pic = currentImage/(pixelsize**2)
scale = max(pic.flatten())

ax = plt.subplot(111,zorder=8)

ax.plot(rVector[:-4]/TOF, density[:-4]/scale, 'ko',markersize=5.5,zorder=1,clip_on=False)


x_all = rVectorAll/TOF
x_pts = rVector/TOF
x_to_0 = np.append(0,x_pts)

fermi_to_0 = np.append(density_fermi[0],density_fermi)
thermal_to_0 = np.append(density_thermal[0],density_thermal)

x_plot = np.linspace(min(x_all),max(x_all),1000)

y_fermi = spline(x_to_0, fermi_to_0, x_plot)
y_thermal = spline(x_to_0, thermal_to_0, x_plot)

h2 = plt.plot(x_plot, y_fermi/scale, 'b',label='Fermi-Dirac',linewidth=1.5,zorder=3)
h1 = plt.plot(x_plot, y_thermal/scale, 'r',label='Thermal',linewidth=1.5,zorder=2)

ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

plt.xlabel('Velocity (mm/s)')
plt.ylabel('Column density (a.u.)')
ax.tick_params(axis='y', which='major', pad=12)

legend = plt.legend(frameon=False, fontsize=12,numpoints=1,loc=3)
plt.ylim(0,1)
plt.xlim(0, V_MAX)
plt.yticks(np.arange(0,1.2,0.2))
plt.gcf().subplots_adjust(bottom=0.15,left=0.15)





pos1 = ax.get_position()
width2 = pos1.width/40.0
pos2 = [pos1.x0-width2, pos1.y0,  width2, pos1.height] 

bar = plt.axes(pos2,zorder=2)
xbar = np.linspace(0,1,5)
ybar = np.linspace(0,1,1000)
xbar, ybar = np.meshgrid(xbar, ybar)

bar.pcolor(xbar,ybar,ybar,linewidth=0,rasterized=True,zorder=2, cmap=COLORMAP)
plt.xticks([])
plt.yticks([])



width3 = 0.3
height3 = 0.375
inset = plt.axes([pos1.x0+pos1.width-width3, pos1.y0+pos1.height-height3, width3, height3],zorder=20)

inset.pcolor(vx, vy, currentImage/(scale*pixelsize**2),linewidth=2,rasterized=True, cmap=COLORMAP)

ax2 = plt.gca()
plt.xlim(-9, 9)
plt.ylim(-9, 9)

inset.xaxis.set_ticks_position('bottom')
inset.yaxis.set_ticks_position('left')

ax2.spines['bottom'].set_color('k')
ax2.spines['top'].set_color('k')
ax2.spines['left'].set_color('k')
ax2.spines['right'].set_color('k')

plt.xticks(color='k',fontsize=12)
plt.yticks(color='k',fontsize=12)

for line in ax2.xaxis.get_ticklines():
    line.set_color('w')
    
for line in ax2.yaxis.get_ticklines():
    line.set_color('w')   

ax2.xaxis.labelpad = 1

plt.gca().set_xlabel('v (mm/s)',fontsize=12)

# plt.savefig('../tof_inset.pdf')


# In[9]:

# MAKE PLOT WITH ERROR BARS

rVectorAll = np.arange(0., R_MAX, R_BIN*pixelsize)
rVector = (rVectorAll[:-1] + rVectorAll[1:])/2
density = np.empty_like(rVector)
density_thermal = np.empty_like(rVector)
density_zero = np.empty_like(rVector)
density_fermi = np.empty_like(rVector)
density_err = np.empty_like(rVector)

noisePerPixel = np.std(currentImage - thermal_fit)


for i, trash in enumerate(rVector):
    ind = (r > rVectorAll[i]) & (r < rVectorAll[i+1])
    density[i] = np.sum(currentImage[ind]/(pixelsize**2)) / np.sum(ind)
    density_err[i] = (noisePerPixel/(pixelsize**2)) / np.sqrt(np.sum(ind))
    density_thermal[i] = (np.sum(thermal_fit[ind])/(pixelsize**2)) / np.sum(ind)
    density_fermi[i] = (np.sum(fermi_fit[ind])/(pixelsize**2)) / np.sum(ind)

fig, (ax, bx) = plt.subplots(2,1,sharex=True, gridspec_kw = {'height_ratios':[4, 1]})
fig.subplots_adjust(hspace=0)
    
    
pic = currentImage/(pixelsize**2)
scale = max(pic.flatten())
scale *= .93

ax.plot(rVector[:-4]/TOF, density[:-4]/scale, 'ko',markersize=5.5,clip_on=False,zorder=22)

x_all = rVectorAll/TOF
x_pts = rVector/TOF
x_to_0 = np.append(0, x_pts)

fermi_to_0 = np.append(density_fermi[0],density_fermi)
thermal_to_0 = np.append(density_thermal[0],density_thermal)

x_plot = np.linspace(min(x_all),max(x_all),1000)

y_fermi = spline(x_to_0, fermi_to_0, x_plot)
y_thermal = spline(x_to_0, thermal_to_0, x_plot)

h2 = ax.plot(x_plot, y_fermi/scale, 'b',label='Fermi-Dirac',linewidth=1.5,zorder=3)
h1 = ax.plot(x_plot, y_thermal/scale, 'r',label='Thermal',linewidth=1.5,zorder=2)

ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

ax.set_ylabel('Column density (a.u.)')
ax.tick_params(axis='y', which='major', pad=12)

legend = ax.legend(frameon=False, fontsize=12,numpoints=1,loc=3)

ax.set_ylim(-0.02,1)
ax.set_yticks([0, .2, .4, .6, .8, 1])
ax.set_xlim(0, V_MAX)
plt.yticks(np.arange(0,1.2,0.2))
plt.gcf().subplots_adjust(bottom=0.15,left=0.2)





pos1 = ax.get_position()
width2 = pos1.width/40.0
pos2 = [pos1.x0-width2, pos1.y0,  width2, pos1.height] 

bar = plt.axes(pos2,zorder=2)
xbar = np.linspace(0,1,5)
ybar = np.linspace(0,1,1000)
xbar, ybar = np.meshgrid(xbar, ybar)

bar.pcolor(xbar,ybar,ybar,linewidth=0,rasterized=True,zorder=2, cmap=COLORMAP)
plt.xticks([])
plt.yticks([])



width3 = 0.3*0.9
height3 = 0.375*0.9
inset = plt.axes([pos1.x0+pos1.width-width3, pos1.y0+pos1.height-height3, width3, height3], 
                 zorder=20)

#inset = plt.axes([.56, .49, .3, .375],zorder=20)
inset.pcolor(vx, vy, currentImage/(scale*pixelsize**2),linewidth=2,rasterized=True, cmap=COLORMAP, vmin=0)
ax2 = plt.gca()

ax2.set_xlim(-9, 9)
ax2.set_ylim(-9, 9)

inset.xaxis.set_ticks_position('bottom')
inset.yaxis.set_ticks_position('left')

ax2.spines['bottom'].set_color('k')
ax2.spines['top'].set_color('k')
ax2.spines['left'].set_color('k')
ax2.spines['right'].set_color('k')

plt.xticks(color='k',fontsize=12)
plt.yticks(color='k',fontsize=12)

for line in ax2.xaxis.get_ticklines():
    line.set_color('w')
    
for line in ax2.yaxis.get_ticklines():
    line.set_color('w')   

ax2.xaxis.labelpad = 1

plt.gca().set_xlabel('v (mm/s)',fontsize=12)


bx.set_xlabel('Velocity (mm/s)')
bx.set_ylabel('Resid.')

bx.set_yticks(np.arange(-0.1,0.0,0.1))
bx.set_ylim(-0.12,0.12)


eb_lw = 8

(_, caps, _) = bx.errorbar(rVector/TOF, (density - density_fermi)/scale, density_err/scale, 
                           fmt=',', mfc='none', markeredgecolor='b', markeredgewidth=1, 
                           capsize=0, color='b', markersize=8, linewidth=eb_lw, zorder=20)
for cap in caps:
    cap.set_markeredgewidth(eb_lw)


(_, caps, _) = bx.errorbar(rVector/TOF, (density - density_thermal)/scale, density_err/scale, 
                           fmt=',', mfc='none', markeredgecolor='r', markeredgewidth=1, 
                           capsize=0, color='r', markersize=8, linewidth=eb_lw, zorder=21)
for cap in caps:
    cap.set_markeredgewidth(eb_lw)
    


x_min,x_max = min(rVector/TOF),max(rVector/TOF)

x_line = np.linspace(x_min-5,x_max+5,1000)
y_line = 0*x_line
bx.plot(x_line,y_line,color='#999999',zorder=1)

bx.yaxis.set_ticks_position('left')

plt.savefig('momentum_distribution.pdf')


# In[292]:

#Errors
noisePerPixel = np.std(currentImage - thermal_fit)

plt.figure(figsize=(6,8))

ax1 = plt.subplot(3,1,1)
plt.errorbar(rVector/TOF, density - density_thermal, density_err, fmt='o', capsize=4)
h1 = plt.plot(rVector/TOF, density_thermal - density_thermal, label='Maxwell-Boltzmann')
h2 = plt.plot(rVector/TOF, density_fermi - density_thermal, label='Fermi-Dirac')
plt.ylabel('Residual Maxwell-Boltzmann ($\mathsf{\mu m^{-2}}$)')
# plt.legend(frameon=False)
ax1.get_xaxis().set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.yaxis.set_ticks_position('left')

ax2 = plt.subplot(3,1,2)
plt.errorbar(rVector/TOF, density - density_fermi, density_err, fmt='o', capsize=4)
h1 = plt.plot(rVector/TOF, density_thermal - density_fermi, label='Maxwell-Boltzmann')
h2 = plt.plot(rVector/TOF, density_fermi - density_fermi, label='Fermi-Dirac')
plt.ylabel('Residual Fermi-Dirac ($\mathsf{\mu m^{-2}}$)')
# plt.legend(frameon=False)
ax2.get_xaxis().set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)
ax2.yaxis.set_ticks_position('left')

ax3 = plt.subplot(3,1,3)
plt.errorbar(rVector/TOF, density, density_err, fmt='o', capsize=4)
h1 = plt.plot(rVector/TOF, density_thermal, label='Maxwell-Boltzmann')
h2 = plt.plot(rVector/TOF, density_fermi, label='Fermi-Dirac')
plt.xlabel('Velocity (mm/s)')
plt.ylabel('Column density ($\mathsf{\mu m^{-2}}$)')
plt.legend(frameon=False)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.xaxis.set_ticks_position('bottom')
ax3.yaxis.set_ticks_position('left')
plt.ylim(-0.2, 8)
plt.text(8, 2, '$T/T_F=%0.2f$' % TTFshape, size=18)
plt.gcf().subplots_adjust(bottom=0.15,left=0.16)
