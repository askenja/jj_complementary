"""
Created on Wed Jul 24 18:42:29 2019

Application of Lallement map to Gaia data. 

@author: Skevja
"""

import os
import numpy as np 
from astropy.table import Table
import healpy as hp
import pandas as pd
import time

t1 = time.time()

# Read the table 
table_name = 'gaia_example_trans'

print('Reading data...',end=' ')
t = Table.read(''.join((table_name,'.csv')))

print('ok.\nCalculating M_G columns...',end=' ')
# Calculate absolute G, G_BP and G_RP
t['M_G'] = t['phot_g_mean_mag'] - 5*np.log10(t['d']) + 5
t['M_BP'] = t['phot_bp_mean_mag'] - 5*np.log10(t['d']) + 5
t['M_RP'] = t['phot_rp_mean_mag'] - 5*np.log10(t['d']) + 5

print('ok.\nGetting extinction...',end=' ')
NSIDE = 16   # resolution of Lallement map 
# Each star in the catalog is sorted into our sky grid (its pixel number is calculated)
# Then we calculate the number of unique pixels (should be NPIX or close to this)
hpix = hp.pixelfunc.ang2pix(NSIDE,np.pi/2+np.deg2rad(t['lat']),np.deg2rad(t['lon']),nest=True)
uhpix = np.unique(hpix)

# Pre-calculate reddening grid 
# (download the reddening curve for each pixel from uhpix)
Egrid = []

delta_d = 5  # pc, distance step of Lallement map 
for i in range(len(uhpix)):
    extinction_table = pd.read_csv(os.path.join('..','Lallement','dustmap_data',
                                                ''.join(('dust_hpix',str(int(uhpix[i])),'.csv'))),
                                   delimiter=';',names=['d','ebv','ed','eebv_min','eebv_max'])
    E_bv_c = [np.float64(k) for k in extinction_table['ebv'][1:]] # [1:] skips header
    Egrid.append(E_bv_c)
Egrid = np.array(Egrid,dtype=object)

# For each star in the catalog we find index of its pixel in the array of uhpix
# and distance index corresponding to LAllement distance grid 
index_h = np.array([np.where(uhpix==i)[0][0] for i in hpix],dtype=np.int32)
index_d = np.array(t['d']//delta_d,dtype=np.int32)

# For each star we get reddening from the dust map 
#----------------------------------------------------------------
# If distance in the catalog is larger than the maxuimum distance available 
# for this line-of-sight in the dust map, we take reddening for the largest available distance
for i in range(len(index_d)):
    if index_d[i]>=len(Egrid[index_h[i]]) or index_d[i]<0:
        index_d[i]=len(Egrid[index_h[i]])-1
        
# In all other cases we simply get reddening inthe direction of (l,b) and at distance d. 
E_bv = np.array([Egrid[i][k] for i,k in zip(index_h,index_d)])  

print('ok.\nColour transformations...',end=' ' )
# Transformation coefficients can be found at http://stev.oapd.inaf.it/cgi-bin/cmd
# (after you submit a request for some isochrone, there will a be a small table 
# at the new page). Just use Gaia passbands.  

A_v = 3.1*E_bv
A_g = 0.83627*A_v
A_bp = 1.08337*A_v
A_rp = 0.63439*A_v
# This was some old check, probably not needed, extinction must be positive all the time. 
A_g[A_g < 0] = 0 
A_bp[A_bp < 0] = 0 
A_rp[A_rp < 0] = 0 

print('ok.\nSaving data...',end=' ')
# And save the table with the new columns
t['phot_g_mean_mag_0l'] = np.subtract(t['phot_g_mean_mag'],A_g)
t['phot_bp_mean_mag_0l'] = np.subtract(t['phot_bp_mean_mag'],A_bp)
t['phot_rp_mean_mag_0l'] = np.subtract(t['phot_rp_mean_mag'],A_rp)
t['M_G_0l'] = np.subtract(t['M_G'],A_g)
t['M_BP_0l'] = np.subtract(t['M_BP'],A_bp)
t['M_RP_0l'] = np.subtract(t['M_RP'],A_rp)
t['A_g_l'] = A_g
t['A_bp_l'] = A_bp
t['A_rp_l'] = A_rp

t.write(''.join((table_name,'_r.csv')),overwrite=True)

print('ok.\nDone.')

print(round((time.time()-t1)/60,2), 'min ==', round((time.time()-t1)/3600,2), 'h')


