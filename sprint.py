import numpy as np
from astropy.table import Table
from surveysim.surveysim import surveySim


import os
import argparse
import yaml

# Run surveysim for a month
run_surveysim = False
if run_surveysim:
    surveySim((2019,9,1), (2019,10,1))

# Read the TILEID that got observed
a = Table.read("obslist_all.fits")
tileid= a['TILEID']
ra = a['RA']
dec = a['DEC']

# This region roughly corresponds to the observed region in September 2019
min_ra = 0.0
max_ra = 40.0
min_dec = -20.0
max_dec = 5.0

# estimate how many tiles are covered by the previous cuts
ii = (ra<max_ra) & (ra>min_ra) & (dec<max_dec) & (dec>min_dec)
tile_in = len(a[ii])
tile_all = len(a)
print('tiles fulllength:', tile_all)
print('tiles ra,dec cut:', tile_in)

#generate targets
import multiprocessing
nproc = multiprocessing.cpu_count()

print('using nprocs {}'.format(nproc))

from desitarget.mock.build import targets_truth
from desispec.log import get_logger, DEBUG

log = get_logger(DEBUG)

config_file = 'mock_input.yaml'
# Read parameters from yaml
log.info('Reading configuration file {}'.format(config_file))
with open(config_file, 'r') as pfile:
    params = yaml.load(pfile)

# Optionally read the "real" target catalog.
realtargets_file = '/project/projectdirs/desi/target/catalogs/targets-dr3.1-0.8.1.fits'
output_dir = "./output"
bricksize = 0.25
outbricksize = 0.50

from astropy.io import fits
print('Loading real targets from {}'.format(realtargets_file))
realtargets = fits.getdata(realtargets_file)


# Construct Targets and Truth files
targets_truth(params, output_dir, realtargets=realtargets, seed=42,
              verbose=True, nproc=nproc, bricksize=bricksize,
              outbricksize=outbricksize)

log.info('All done!')

