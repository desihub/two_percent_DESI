#!/usr/bin/env python

"""
Run redrock by hand for DC17a (2% sprint)
"""

from __future__ import absolute_import, division, print_function
from mpi4py import MPI
import sys, os, glob, time
import numpy as np
from redrock.external import desi

#- run from /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

def get_subdir(pix):
    superpix = pix // 64
    return 'spectra/8-{superpix}/64-{pix}'.format(superpix=superpix, pix=pix)

def get_outfiles(pix):
    subdir = get_subdir(pix)
    rrout = '{subdir}/rr-64-{pix}.h5'.format(subdir=subdir, pix=pix)
    zbout = '{subdir}/zbest-64-{pix}.fits'.format(subdir=subdir, pix=pix)
    return rrout, zbout

if rank == 0:
    t0 = time.time()
    print('Starting at {}'.format(time.asctime()))
    pixels = list()
    pixdirs = sorted(glob.glob('spectra/8-*/64-*'))
    for dirname in pixdirs:
        pixnum = int(os.path.basename(dirname)[3:])
        rrout, zbout = get_outfiles(pixnum)
        if os.path.exists(rrout) and os.path.exists(zbout):
            print('skipping completed {}'.format(pixnum))
        else:
            superpix = pixnum // 64
            specfiles = glob.glob('spectra/8-{}/64-{}/spectra*'.format(superpix, pixnum))
            if len(specfiles) > 0:
                pixels.append(pixnum)
            else:
                print('Skipping pix {} with no specfiles'.format(pixnum))

    print('{}/{} pix left to do'.format(len(pixels), len(pixdirs)))
    print('Initial setup took {:.1f} sec'.format(time.time() - t0))
else:
    pixels = None

sys.stdout.flush()
pixels = comm.bcast(pixels, root=0)

for pix in pixels[rank::size]:
    t0 = time.time()
    print('---- rank {} pix {} {}'.format(rank, pix, time.asctime()))
    sys.stdout.flush()
    rrout, zbout = get_outfiles(pix)
    cmd = 'rrdesi -o {} --zbest {}'.format(rrout, zbout)
    
    subdir = get_subdir(pix)

    for specfile in sorted(glob.glob('{}/spectra-*.fits'.format(subdir))):
        cmd = cmd + ' ' + specfile
    print('RUNNING', cmd)
    try:
        dt0 = time.time() - t0
        if dt0 > 2:
            print('long setup for pix {} rank {} = {} sec'.format(pix, rank, dt0))
        t1 = time.time()
        ### desi.rrdesi(cmd.split()[1:])
        os.system(cmd)
        dt1 = time.time() - t1
        print('FINISHED pix {} rank {} in {:.1f} sec'.format(pix, rank, dt0+dt1))
    except Exception as err:
        print('FAILED: pix {} rank {}'.format(pix, rank))
        import traceback
        traceback.print_exc()

print('---- rank {} is done'.format(rank))
sys.stdout.flush()

comm.barrier()
if rank == 0:
    print('all done')
