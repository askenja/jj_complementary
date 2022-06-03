"""
Created on Wed Jul 24 18:42:29 2019

Application of (Green + Lallement) combined map to Gaia data. 

@author: Skevja
"""

import numpy as np 
from astropy.table import Table
from astropy.coordinates import SkyCoord
import astropy.units as u
from dustmaps.bayestar import BayestarQuery
import time 

t1 = time.time()

table_name = 'gaia_example_trans_r'

print('Reading data...',end=' ')
t = Table.read(''.join((table_name,'.csv')))

print('ok.\nCreating coordinates...',end=' ')
coords = SkyCoord(t['lon']*u.deg,t['lat']*u.deg,
                  distance=t['d']*u.pc,frame='galactic')

print('ok.\nGetting extinction...',end=' ')
bayestar = BayestarQuery(max_samples=1)
A_v = 2.742*bayestar(coords)

print('ok.\nColour transformations...',end=' ' )
# Transformation coefficients can be found at http://stev.oapd.inaf.it/cgi-bin/cmd
# (after you submit a request for some isochrone, there will a be a small table 
# at the new page). Just use Gaia passbands.  

A_g = 0.83627*A_v
A_bp = 1.08337*A_v
A_rp = 0.63439*A_v
# This was some old check, probably not needed, extinction must be positive all the time. 
A_g[A_g < 0] = 0 
A_bp[A_bp < 0] = 0 
A_rp[A_rp < 0] = 0 

print('ok.\nSaving data...',end=' ')
# And save the table with new columns
t['phot_g_mean_mag_0g'] = np.subtract(t['phot_g_mean_mag'],A_g)
t['phot_bp_mean_mag_0g'] = np.subtract(t['phot_bp_mean_mag'],A_bp)
t['phot_rp_mean_mag_0g'] = np.subtract(t['phot_rp_mean_mag'],A_rp)
t['M_G_0g'] = np.subtract(t['M_G'],A_g)
t['M_BP_0g'] = np.subtract(t['M_BP'],A_bp)
t['M_RP_0g'] = np.subtract(t['M_RP'],A_rp)
t['A_g_g'] = A_g
t['A_bp_g'] = A_bp
t['A_rp_g'] = A_rp

# We combine two maps: when A=0 in Green map, we use extinction from Lallement. 
# G
t['phot_g_mean_mag_0gl'] = t['phot_g_mean_mag_0g']
t['phot_g_mean_mag_0gl'][t['A_g_g']==0] = t['phot_g_mean_mag_0l']
t['M_G_0gl'] = t['M_G_0g']
t['M_G_0gl'][t['A_g_g']==0] = t['M_G_0l']
# BP
t['phot_bp_mean_mag_0gl'] = t['phot_bp_mean_mag_0g']
t['phot_bp_mean_mag_0gl'][t['A_bp_g']==0] = t['phot_bp_mean_mag_0l']
t['M_BP_0gl'] = t['M_BP_0g']
t['M_BP_0gl'][t['A_bp_g']==0] = t['M_BP_0l']
# RP
t['phot_rp_mean_mag_0gl'] = t['phot_rp_mean_mag_0g']
t['phot_rp_mean_mag_0gl'][t['A_rp_g']==0] = t['phot_rp_mean_mag_0l']
t['M_RP_0gl'] = t['M_RP_0g']
t['M_RP_0gl'][t['A_rp_g']==0] = t['M_RP_0l']

t.write(''.join((table_name,'_r.csv')),overwrite=True)

print('ok.\nDone.')

print(round((time.time()-t1)/60,2), 'min ==', round((time.time()-t1)/3600,2), 'h')

