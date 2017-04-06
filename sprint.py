import numpy as np
from surveysim.surveysim import surveySim
import os
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument('--first', '-f', help='first grid', type=int, default=None)
parser.add_argument('--last', '-l', help='last grid', type=int, default=None)
args = parser.parse_args()


# Read the TILEID that got observed
a = np.loadtxt('twopct.ecsv', skiprows=19, usecols=(4,5,6))
tileid= np.int_(a[:,0])
ra = a[:,1]
dec = a[:,2]

side_grid = 2.0
n_tiles = len(a)
grid_list = []
for i in range(n_tiles):
    ra_grid = int(ra[i] - ra[i]%side_grid)
    dec_grid = int(dec[i] - dec[i]%side_grid)
    if (ra_grid, dec_grid) not in grid_list:
        grid_list.append((ra_grid,dec_grid))

n_grid = len(grid_list)
print('n_tiles', n_tiles)
print('n_grid', n_grid)

generate_spec = True

first_grid= args.first
last_grid = min(args.last, n_grid)
for grid_i in range(first_grid, last_grid):
    pair = grid_list[grid_i]
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
    
        if not os.path.exists(output_dir):    
            # Construct Targets and Truth files
            targets_truth(params, output_dir, realtargets=realtargets, seed=42,
                          verbose=True, nproc=nproc, bricksize=bricksize,
                          outbricksize=outbricksize)

        log.info('All done!')

print('n_tiles', n_tiles)
print('n_grid', len(grid_list))
