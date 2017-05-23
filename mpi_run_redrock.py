#!/usr/bin/env python

"""
Run redrock by hand for DC17a (2% sprint)
"""

from __future__ import absolute_import, division, print_function
from mpi4py import MPI
import sys, os, glob
import numpy as np
from redrock.external import desi

#- run from /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    bricks = list()
    for brickfile in sorted(glob.glob('bricks/*/brick-b-*.fits')):
        #- extract brickname from /path/to/{brickname}/brick-b-{brickname}.fits
        brickname = brickfile[-13:-5]

        rrout = 'redrock/rr-{}.h5'.format(brickname)
        zbout = 'redrock/zbest-{}.fits'.format(brickname)
        if os.path.exists(rrout) and os.path.exists(zbout):
            print('skipping completed {}'.format(brickname))
        else:
            bricks.append(brickname)
else:
    bricks = None

sys.stdout.flush()
bricks = comm.bcast(bricks, root=0)

for brickname in bricks[rank::size]:
    print('---- rank {} {}'.format(rank, brickname))
    sys.stdout.flush()
    rrout = 'redrock/rr-{}.h5'.format(brickname)
    zbout = 'redrock/zbest-{}.fits'.format(brickname)
    cmd = 'rrdesi -o {} --zbest {}'.format(rrout, zbout)
    for brickfile in glob.glob('bricks/{}/brick-*.fits'.format(brickname)):
        cmd = cmd + ' ' + brickfile
    #print(cmd)
    desi.rrdesi(cmd.split()[1:])
        
