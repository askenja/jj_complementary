"""
Created on Fri May  4 17:06:07 2018

Sky grid for dust map. 

@author: skevja
"""

import numpy as np
import healpy as hp 
from matplotlib import pyplot as plt
from astropy import units as u
from astropy.coordinates import SkyCoord
from healpy import mollview, graticule

# Setting parameters and creating the grid
# ---------------------------------------------------------------

NSIDE = 16                          # defines map resolution, must be a power of 2 
NPIX = hp.nside2npix(NSIDE)         # number of pixels corresponding to the chosen resolution
hpixels = np.arange(NPIX)           # creates array with pixels' indices 
print('Number of pixels: ', NPIX)

hangles = hp.pix2ang(NSIDE,hpixels, # creates (co)latitude and longitude for each pixel; 
                     nest=True)     # pixels are arranged acconding to the 'nested' scheme
                                                

# Convert healpy angles to Galactic lon and lat. 
# For details, see https://healpy.readthedocs.io/en/latest/tutorial.html
l, b = np.rad2deg(hangles[1]), np.rad2deg(hangles[0]) - 90 
lb_coords = SkyCoord(l*u.deg, b*u.deg,frame='galactic')
                  
# And get equatorial coordinates: 
eq_coords = lb_coords.transform_to('icrs')
ra,dec = eq_coords.ra.value, eq_coords.dec.value


# Save the grid and make a plot
# ---------------------------------------------------------------
head = 'HEALPIX, lon [deg], lat [deg], ra[deg], dec[deg]; ordering scheme = nested'
np.savetxt('healpix_grid.csv',np.stack((hpixels,l,b,ra,dec),axis=-1),header=head,delimiter=',')


plt.figure(figsize=(10,7))
mollview(hpixels,coord=['G'],nest = True,cmap='viridis',min=0,max=int(NPIX),
         notext=True,fig=1,cbar=True,hold=True,title='Sky map for the dust grid (galactic)')
graticule()
plt.savefig('healpix_grid.png')
