#!/usr/bin/env python

"""
Fix spectra and zbest keywords to match what we wish we had done :)

spectra header keywords:
- HPXNSIDE
- HPXNEST

spectra fibermap columns:
- TILEID
- HPXPIXEL

For testing:
cd $SCRATCH/temp/dc17a-test/
cp -r /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a2/spectra-64/102 spectra-64/

fitsdiff spectra-64/102/10237/spectra-64-10237.fits /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a2/spectra-64/102/10237/spectra-64-10237.fits 
"""

from __future__ import absolute_import, division, print_function
import sys, os
import numpy as np
import fitsio
from astropy.io import fits
from glob import glob

reduxdir = sys.argv[1]
specfiles = sorted(glob(reduxdir+'/spectra-64/*/*/spectra*.fits'))
print('{} spectra files found'.format(len(specfiles)))
if len(specfiles) == 0:
    sys.exit(1)

#- Build a map of (NIGHT,EXPID) -> TILEID
# print('Building (NIGHT, EXPID) -> TILEID map')
# simdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/sim/dc17a2'
# tilemap = dict()
# for simspecfile in glob(simdir+'/*/simspec*.fits'):
#     with fitsio.FITS(simspecfile) as fx:
#         if 'OBSCONDITIONS' in fx:
#             hdr = fx[0].read_header()
#             expid = hdr['EXPID']
#             night = hdr['NIGHT']
#             tileid = fx['OBSCONDITIONS']['TILEID'][0][0]
#             tilemap[(night, expid)] = tileid

#- for testing
# filename = '/scratch2/scratchdirs/sjbailey/temp/dc17a-test/spectra-64/102/10237/spectra-64-10237.fits'

#- Loop over filenames
for filename in specfiles:
    print(filename)
    #- updating keywords is easier with astropy.io.fits
    print('  Updating keywords')
    pix = int(os.path.splitext(os.path.basename(filename))[0].split('-')[-1])
    fx = fits.open(filename, mode='update', memmap=False)
    fx[0].header['HPXPIXEL'] = (pix, 'healpix pixel using NESTED ordering')
    fx[0].header['HPXNSIDE'] = (64, 'healpix nside')
    fx[0].header['HPXNEST'] = (True, 'healpix NESTED ordering (not RING)')

    for key in ['EXPID', 'NIGHT', 'AIRMASS', 'EXPTIME', 'DATE-OBS', 'BUNIT']:
        if key in fx[0].header:
            del fx[0].header[key]

    fx.flush()
    fx.close()

    #- inserting a new column is easier with fitsio
    #- Oddly variable in speed; skipping

    # fx = fitsio.FITS(filename, mode='rw')
    # if 'HPXPIXEL' not in fx['FIBERMAP'].get_colnames():
    #     print('  Adding HPXPIXEL column to FIBERMAP')
    #     pix = int(os.path.splitext(os.path.basename(filename))[0].split('-')[-1])
    #     hpxpixel = np.ones(fx['FIBERMAP'].get_nrows(), dtype='i4') * pix
    #     fx['FIBERMAP'].insert_column('HPXPIXEL', hpxpixel)

    # if 'TILEID' not in fx['FIBERMAP'].get_colnames():
    #     print('  Adding TILEID column to FIBERMAP')
    #     fmap = fx['FIBERMAP'].read()
    #     tileid = np.zeros(len(fmap), dtype='i4')
    #     for i, (night, expid) in enumerate(zip(fmap['NIGHT'], fmap['EXPID'])):
    #         tileid[i] = tilemap[(night,expid)]
    #     fx['FIBERMAP'].insert_column('TILEID', tileid)
    #
    # fx.close()

#-------------------------------------------------------------------------


