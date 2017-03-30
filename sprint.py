import numpy as np
from astropy.table import Table
from surveysim.surveysim import surveySim

# Run surveysim for a month
run_surveysim = False
if run_surveysim:
    surveySim((2019,9,1), (2019,10,1))

# Select the TILEID that got observed

a = Table.read("obslist_all.fits")
tileid= a['TILEID']
ra = a['RA']
dec = a['DEC']

#print('DEC counts', stats.itemfreq(np.int_(np.array(a['DEC']))))
#print('RA counts', stats.itemfreq(np.int_(np.array(a['RA']))))

min_ra = 0.0
max_ra = 40.0
min_dec = -20.0
max_dec = 5.0

ii = (ra<max_ra) & (ra>min_ra) & (dec<max_dec) & (dec>min_dec)
tile_in = len(a[ii])
tile_all = len(a)
print('tiles fulllength:', tile_all)
print('tiles ra,dec cut:', tile_in)
