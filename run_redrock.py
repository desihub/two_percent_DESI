#!/usr/bin/env python

"""
Run redrock by hand for DC17a (2% sprint)
"""

from __future__ import absolute_import, division, print_function
import sys, os, glob
import numpy as np
from redrock.external import desi

#- run from /scratch2/scratchdirs/sjbailey/desi/dc17a/spectro/redux/dc17a

bricks = list()
for brickfile in glob.glob('bricks/*/brick-b-*.fits'):
    #- extract brickname from /path/to/{brickname}/brick-b-{brickname}.fits
    bricks.append(brickfile[-13:-5])

todo = list()
for brickname in sorted(bricks):
    rrout = 'redrock/rr-{}.h5'.format(brickname)
    zbout = 'redrock/zbest-{}.fits'.format(brickname)
    if os.path.exists(rrout) and os.path.exists(zbout):
        print('---- skipping completed brick {}'.format(brickname))
    else:
        print('---- '+brickname)
        cmd = 'rrdesi -o {} --zbest {}'.format(rrout, zbout)
        for brickfile in glob.glob('bricks/{}/brick-*.fits'.format(brickname)):
            cmd = cmd + ' ' + brickfile
        #print(cmd)
        desi.rrdesi(cmd.split()[1:])
        
