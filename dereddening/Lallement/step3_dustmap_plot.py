"""
Created on Fri May  4 13:49:38 2018

Visualization of Lallement dust map. 

@author: skevja
"""
import os
import numpy as np
from healpy import mollview, graticule
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import time


t1 = time.time()

# Some preparations
# ---------------------------------------------------------------

dir_out = 'dustmap_data'                               # folder with dust map 
grid = np.loadtxt('healpix_grid.csv',delimiter=',')    # corresponding sky grid 
hpix = grid.T[0]  # pixel number
l = grid.T[1]     # longitude, [0,360] deg
b = grid.T[2]     # latitude, [-90,90] deg

NPIX = len(hpix)  # number of pixels
dmax = 400        # pc, up to this distance we integrate the reddening 


# Construct the map
# ---------------------------------------------------------------

E_bv = np.zeros((NPIX))

count_short = 0 

for i in range(NPIX):
    # read the table
    t = pd.read_csv(os.path.join(dir_out,
                                 ''.join(('dust_hpix',str(int(hpix[i])),'.csv'))),delimiter=';')
    index = np.where(abs(t['distance']-dmax)==np.amin(abs(t['distance']-dmax)))[0]
    delta_d = np.float64(np.abs(t['distance'][index] - dmax))
    if delta_d > 50: 
        print(i, 'Map l-o-s shorter than dmax, d_max_map = ',np.amax(t['distance']),' pc')
        count_short += 1 
    E_bv[i] = t['reddening'][index]
    if i%100==0:
        print(i)


print('\n',round(count_short/NPIX*100,1),
      '% of pixels have shorter maximum distance than dmax')

# Plot
# ---------------------------------------------------------------

# Define color map  
cmap = mpl.cm.get_cmap("Greys").copy()
cmap.set_over('w')
cmap.set_under('w')
cmap.set_bad('w')

fig = plt.figure(figsize=(10,8))
mollview(E_bv,coord=['G'],nest=True,cmap=cmap,min=0,max=round(max(E_bv),1),notext=True,fig=1, 
         cbar=False,title='$\mathrm{d = }$'+str(dmax)+'$\mathrm{\  pc}$')
graticule()

cax = fig.add_axes([0.125, 0.15, 0.775, 0.03])
cb = mpl.colorbar.ColorbarBase(cax,cmap=cmap,
                               norm = mpl.colors.Normalize(vmin=0, vmax=round(max(E_bv),1)),  
#                               format='%0.5f'
#                               ticks=bound,
                               orientation='horizontal')
cb.set_label(r'$\mathrm{E(B-V)}$',fontsize=12)
cb.solids.set_edgecolor("face")
plt.show()
plt.savefig(''.join(('lallement_dustmap_d',str(dmax),'pc.png')))


print(round((time.time()-t1)/60,2), 'min ==', round((time.time()-t1)/3600,2), 'h')

