"""
Created on Fri May  4 13:49:38 2018

Downloads dust map from Stilism website. 

@author: skevja
"""

import os
import numpy as np
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

t1 = time.time()

#==============================================================================
# Some preparations
#==============================================================================

dir_out = 'dustmap_data'            # output directory (if does not exist, will be created)
if not os.path.isdir(dir_out):
    os.mkdir(dir_out)
    
file_name_default = 'reddening.csv' # default name of the file from Stilism website
grid = np.loadtxt('healpix_grid.csv',delimiter=',')  # Sky grid created at the previous step
hpix = grid.T[0]    # pixel number
l = grid.T[1]     # longitude, [0,360] deg
b = grid.T[2]     # latitude, [-90,90] deg

NPIX = len(hpix)    # number of pixels


# Configure Firefox profile
# ---------------------------------------------------------------
opt = Options()
opt.set_preference("browser.download.folderList",2) # 2 stands for custom download directory
opt.set_preference("browser.download.dir",os.path.join(os.getcwd(),dir_out)) 
opt.set_preference("browser.download.manager.showWhenStarting",False)
opt.set_preference("browser.helperApps.neverAsk.saveToDisk","text/html,text/csv,text/plain") 
# The last two lines supress pop-up download dialog 

srv = Service('./geckodriver')
browser = Firefox(service=srv,options=opt)


#==============================================================================
# Main part
#==============================================================================

browser.get('http://stilism.obspm.fr/')     # this will open the website

# And we retrieve reddening for all (l,b) pairs
for i in range(NPIX):
    
    print(i,end=' ')
    
    # find and fill l and b fields in the query form
    lon_field = browser.find_element(by=By.NAME,value='vlong')
    lat_field = browser.find_element(by=By.NAME,value='vlat')
    lon_field.clear()
    lat_field.clear()
    lon_field.send_keys(str(l[i])) 
    lat_field.send_keys(str(b[i])) 
    
    # submit the request
    python_button = browser.find_element(by=By.XPATH,
                                         value="//*[contains(text(), 'Submit')]")
    python_button.click()
    
    # download the result and go back to the query form
    python_button = browser.find_element(by=By.XPATH,
                                         value="//*[contains(text(),'Export data to CSV file')]")
    python_button.click()
    print('downloaded')
    
    # rename the file (will include number of pixel)
    file_name_custom = ''.join(('dust_hpix',str(int(hpix[i])),'.csv'))
    w = 10
    while w>0:       
        try:
            os.rename(os.path.join(dir_out,file_name_default), 
                      os.path.join(dir_out,file_name_custom))
            w = 0
        except OSError:
            time.sleep(5)    
            w = w-1.01
    if w < 0:
        print('Slow internet connection, try later.')
        break
    browser.back()    
    
    # close and reopen browser for every N queries 
    # (to prevent browser freezing)
    if i%25==0 and i!=0: 
        browser.close()
        browser = Firefox(service=srv,options=opt)
        browser.get('http://stilism.obspm.fr/')

browser.close()

print('done.')

print(round((time.time()-t1)/60,2), 'min ==', round((time.time()-t1)/3600,2), 'h')

