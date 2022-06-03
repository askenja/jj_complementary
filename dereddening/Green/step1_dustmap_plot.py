"""
Created on Fri May  4 13:49:38 2018

Visualization of Green dust map. 

@author: skevja
"""

import numpy as np
import healpy as hp
from healpy import mollview, graticule
import matplotlib.pyplot as plt
import matplotlib as mpl
from astropy import units as u
from astropy.coordinates import SkyCoord
from dustmaps.bayestar import BayestarQuery
import time


t1 = time.time()

# Some preparations 
# ---------------------------------------------------------------

nside = 16                                  # map resolution 
hpix = np.arange(hp.nside2npix(nside))      # array with pixels' numbers
NPIX = len(hpix)                            # number of pixels

dmax = 1500      # pc, up to this distance we integrate the reddening 


# Get coordinates and retrieve the map 
# ---------------------------------------------------------------

# We can convert pixels' numbers directly to Galactic lon and lat:
hangles = hp.pix2ang(nside,hpix,nest=True,lonlat=True)  
l, b = hangles[0], hangles[1]

lb_coords = SkyCoord(l*u.deg, b*u.deg,distance=dmax*u.pc, frame='galactic')
              
bayestar = BayestarQuery(max_samples=1)

# Bayestar19 reports reddening in an arbitrary unit that can be converted to extinction 
# in different bands using the coefficients given in Table 1 of 
# Green, Schlafly, Finkbeiner et al. (2019).
E_bv = 2.742/3.1*bayestar(lb_coords)


# Define color map  
cmap = mpl.cm.get_cmap("Greys").copy()
cmap.set_over('w')
cmap.set_under('w')
cmap.set_bad('w')

# Visualize the map
# ---------------------------------------------------------------

fig = plt.figure(figsize=(10,8))
mollview(E_bv,coord=['G'],nest =True,cmap=cmap,min=0,max=round(max(E_bv),1),notext=True,fig=1, 
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
fig.show()
plt.savefig(''.join(('green_dustmap_d',str(dmax),'pc.png')))



print(round((time.time()-t1)/60,2), 'min ==', round((time.time()-t1)/3600,2), 'h')

