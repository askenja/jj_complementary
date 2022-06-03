#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 13:40:01 2022

@author: skevja
"""

from jjmodel.transform import XVTrans


# Example 1
# 3D information (coordinates, no radial velocities and proper motions)
# --------------------------------------------------------------------------
# If you give parallaxes, distances will be 1/parallax. 
# When parallax<0, the output quantites which depend on parallaxes are set to nan.
# Instead of parallaxes, you can give distance column ('dpc' and 'edpc' - distance and its error in pc, 
# 'dkpc' and 'edkpc' - distance and its error in kpc). 
 
v = XVTrans('gaia_example','csv',
            {'pm_sgrA':6.37,'epm_sgrA':0.02,                    # Sgr A* proper motion and its uncertainty, mas/yr
             'Usun':11,'Vsun':12.5,'Wsun':7.25,'eUsun':0.5,'eVsun':2,'eWsun':0.5,  # Solar peculiar velocity, km/s 
             'Rsun':8.17,'Zsun':20,'eRsun':0.0013,'eZsun':3})                   # Solar position (R,z) in (kpc,pc)

# Calculate Galactic coordinates (R,phi,z) and (x,y,z) from (ra, dec) in deg and parallax in mas
# Input format: 'ra':'name_of_ra_column' 
v.calc_3d_gal({'ra':'ra','dec':'dec','parallax':'parallax'})   
# Calculate coordinate errors  
v.calc_3d_err({'ra':'ra','dec':'dec','parallax':'parallax','eparallax':'parallax_error'})
# Output is always 'initial_name_of_table'+'_trans'
v.save_result()


# Example 2
# 6D information (coordinates, proper motions and radial velocities)
# --------------------------------------------------------------------------

v = XVTrans('gaia_example','csv',
            {'pm_sgrA':6.37,'epm_sgrA':0.02,
             'Usun':11,'Vsun':4,'Wsun':7.25,'eUsun':0.5,'eVsun':2,'eWsun':0.5,
             'Rsun':8.17,'Zsun':0,'eRsun':0.0013,'eZsun':3})
# Calculate (R,phi,z), (x,y,z) and (Vr,Vphi,Vz), (U,V,W)
v.calc_6d_gal({'ra':'ra','dec':'dec','parallax':'parallax','pmra':'pmra','pmdec':'pmdec','vr':'radial_velocity'})
# Calculate coordinate and velocity errors  
v.calc_6d_err({'ra':'ra','dec':'dec','parallax':'parallax','pmra':'pmra','pmdec':'pmdec','vr':'radial_velocity',
               'era':'ra_error','edec':'dec_error','epmra':'pmra_error','epmdec':'pmdec_error',
               'eparallax':'parallax_error','evr':'radial_velocity_error'})
v.save_result()


# Example 3
# 6D information (coordinates, proper motions and radial velocities) + covariance matrix
# ---------------------------------------------------------------------------------------
# If you use distances which are not 1/parallax, 
# (column 'dpc' or 'dkpc' instead of 'parallax' # in calc_6d_gal), 
# remove from cov_matrix below all correlation coefficients which include index 5, i.e., are related to parallax. 

v = XVTrans('gaia_example','csv',
            {'pm_sgrA':6.37,'epm_sgrA':0.02,
             'Usun':11,'Vsun':4,'Wsun':7.25,'eUsun':0.5,'eVsun':2,'eWsun':0.5,
             'Rsun':8.17,'Zsun':0,'eRsun':0.0013,'eZsun':3})
# Calculate (R,phi,z), (x,y,z) and (Vr,Vphi,Vz), (U,V,W)
v.calc_6d_gal({'ra':'ra','dec':'dec','parallax':'parallax','pmra':'pmra','pmdec':'pmdec','vr':'radial_velocity'})
# Calculate coordinate and velocity errors (with cross-correlations between quantities taken into account)
# Note, sometimes uncertainties with correlations cannot be calculated (equations return nan, 
# maybe adopted approximation is not good enough for some sources), in this case a standard uncertainty 
# without correlations will be written to the output
v.calc_6d_err({'ra':'ra','dec':'dec','parallax':'parallax','pmra':'pmra','pmdec':'pmdec','vr':'radial_velocity',
               'era':'ra_error','edec':'dec_error','epmra':'pmra_error','epmdec':'pmdec_error',
               'eparallax':'parallax_error','evr':'radial_velocity_error'},
               cov_matrix={'c12':'ra_dec_corr','c13':'ra_pmra_corr','c14':'ra_pmdec_corr','c15':'ra_parallax_corr',
                           'c23':'dec_pmra_corr','c24':'dec_pmdec_corr','c25':'dec_parallax_corr',
                           'c34':'pmra_pmdec_corr','c35':'parallax_pmra_corr','c45':'parallax_pmdec_corr'})
v.save_result() 


