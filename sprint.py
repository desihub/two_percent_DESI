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

side_grid = 3.0
n_tiles = len(a)
grid_list = []
for i in range(n_tiles):
    ra_grid = int(ra[i] - ra[i]%side_grid)
    dec_grid = int(dec[i] - dec[i]%side_grid)
    if (ra_grid, dec_grid) not in grid_list:
        grid_list.append((ra_grid,dec_grid))

print('n_tiles', n_tiles)
print('n_grid', len(grid_list))

grid_i = 0
for pair in grid_list:
    grid_i = grid_i + 1 
    min_ra = pair[0]
    min_dec = pair[1]
    print(min_ra, min_dec)
    config_file = 'mock_input.yaml'
    with open(config_file, 'r') as pfile:
        params = yaml.load(pfile)
    params['subset']['min_ra'] = min_ra 
    params['subset']['max_ra'] = min_ra + side_grid
    params['subset']['min_dec'] = min_dec 
    params['subset']['max_dec'] = min_dec + side_grid 
    output_dir = "./output_{}".format(grid_i)  
    print('minra', params['subset']['min_ra'])
    print('maxra', params['subset']['max_ra'])
    print('mindec', params['subset']['min_dec'])
    print('maxdec', params['subset']['max_dec'])
    print('output_dir {}'.format(output_dir))


    
    #generate targets
    generate_spec = True
    if generate_spec:
        nproc = 24

        from desitarget.mock.build import targets_truth
        from desispec.log import get_logger, DEBUG

        log = get_logger(DEBUG)

        # Optionally read the "real" target catalog.
        realtargets_file = '/project/projectdirs/desi/target/catalogs/targets-dr3.1-0.8.1.fits'
        
        bricksize = 0.25
        outbricksize = 0.25
    
        from astropy.io import fits
        print('Loading real targets from {}'.format(realtargets_file))
        realtargets = fits.getdata(realtargets_file)
    
    
        # Construct Targets and Truth files
        targets_truth(params, output_dir, realtargets=realtargets, seed=42,
                      verbose=True, nproc=nproc, bricksize=bricksize,
                      outbricksize=outbricksize)

        log.info('All done!')

