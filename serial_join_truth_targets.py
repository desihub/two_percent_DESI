#!/usr/bin/env python

"""
Serial combining targets
"""

from __future__ import absolute_import, division, print_function
import sys, os, glob
import numpy as np
import fitsio

basedir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets'
indir = basedir
outdir = basedir + '/testmerge'

def mergefiles(infiles, ext, outfile):
    data = list()
    for i, filename in enumerate(infiles):
        if i%100 == 0:
            print('{}/{}'.format(i, len(infiles)))
        data.append(fitsio.read(filename, ext))
    
    tmpout = outfile + '.tmp'
    data = np.hstack(data)
    header = fitsio.read_header(infiles[0], ext)
    fitsio.write(tmpout, data, header=header, clobber=True)
    os.rename(tmpout, outfile)

if not os.path.exists(outdir+'/targets.fits'):
    targetfiles = glob.glob(indir+'/???/targets-*.fits')
    mergefiles(targetfiles, 1, outdir+'/targets.fits')

if not os.path.exists(outdir+'/truth.fits'):
    truthfiles = glob.glob(indir+'/???/truth-*.fits')
    mergefiles(truthfiles, 'TRUTH', outdir+'/truth.fits')
