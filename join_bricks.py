#!/usr/bin/env python

"""
Merge partial brick files into complete bricks

source /project/projectdirs/desi/software/desi_environment.sh
cd $SCRATCH/desi/code/two_percent_DESI
salloc -N 4 -p debug
srun -n 32 -c 3 ./join_bricks.py --indir INDIR --outdir OUTDIR
"""

from __future__ import absolute_import, division, print_function
from mpi4py import MPI
import sys, os
from glob import glob
import shutil
import time

import numpy as np
import fitsio

def mergetruth(infiles, outfile):
    outtmp = outfile + '.tmp'
    if len(infiles) > 1:
        wavehdr = fitsio.read_header(infiles[0], 'WAVE')
        fluxhdr = fitsio.read_header(infiles[0], 'FLUX')
        truthhdr = fitsio.read_header(infiles[0], 'TRUTH')

        wave = [fitsio.read(x, 'WAVE') for x in infiles]
        flux = [fitsio.read(x, 'FLUX') for x in infiles]
        truth = [fitsio.read(x, 'TRUTH') for x in infiles]

        fitsio.write(outtmp, wave[0], extname='WAVE', header=wavehdr, clobber=True)
        fitsio.write(outtmp, np.vstack(flux), header=fluxhdr, extname='FLUX')
        fitsio.write(outtmp, np.hstack(truth), header=truthhdr, extname='TRUTH')
    else:
        shutil.copy(infiles[0], outtmp)

    os.rename(outtmp, outfile)

def mergetargets(infiles, outfile):
    outtmp = outfile + '.tmp'
    if len(infiles) > 1:
        header = fitsio.read_header(infiles[0])
        targets = [fitsio.read(x, 1) for x in infiles]
        fitsio.write(outtmp, np.hstack(targets), header=header)
    else:
        shutil.copy(infiles[0], outtmp)

    os.rename(outtmp, outfile)

#-------------------------------------------------------------------------
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

import optparse

parser = optparse.OptionParser(usage = "%prog [options]")
parser.add_option("-i", "--indir", type=str,  help="input directory")
parser.add_option("-o", "--outdir", type=str,  help="output directory")

opts, args = parser.parse_args()

#- Edison defaults for debugging convenience
if opts.indir is None:
    opts.indir = '/global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI'

if opts.outdir is None:
    opts.outdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a'

#- Build dictionary of files associated with each brickname;
#- use rank 0 only to not overwhelm disk
if rank == 0:
    print('Scanning input truth files', time.asctime())
    truthfiles = glob(opts.indir+'/output_*/???/truth-*.fits')

    bricks = dict()
    for filename in truthfiles:
        brickname = os.path.basename(filename)[6:14]
        if brickname not in bricks:
            bricks[brickname] = [filename, ]
        else:
            bricks[brickname].append(filename)
else:
    bricks = None

#- Broadcast brick dictionary to all ranks
comm.barrier()
if rank == 0:
    print('Broadcasting brick dictionary', time.asctime())

bricks = comm.bcast(bricks, root=0)
bricknames = sorted(bricks.keys())

#- Create output subdirectories using rank 0 process
if rank == 0:
    prefixes = set([b[0:3] for b in bricknames])
    print('Creating output subdirectories', time.asctime())
    print('{} prefixes for {} bricks'.format(len(prefixes), len(bricknames)))
    for p in prefixes:
        subdir = os.path.join(opts.outdir, p)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

#- Start processing bricks
for i in range(rank, len(bricknames), size):
    brickname = bricknames[i]
    subdir = os.path.join(opts.outdir, brickname[0:3])

    print('Rank {}: {}/{} brickname {}'.format(rank, i, len(bricknames), bricknames[i]))
    truthfiles = bricks[brickname]
    outtruth = os.path.join(subdir, 'truth-{}.fits'.format(brickname)) 
    if not os.path.exists(outtruth):
        mergetruth(truthfiles, outtruth)
    else:
        print('    Skipping {}'.format(os.path.basename(outtruth)))

    targetfiles = [x.replace('/truth-', '/targets-') for x in truthfiles]
    outtargets = os.path.join(subdir, 'targets-{}.fits'.format(brickname)) 
    if not os.path.exists(outtargets):
        mergetargets(targetfiles, outtargets)
    else:
        print('    Skipping {}'.format(os.path.basename(outtargets)))

    sys.stdout.flush()

#- Wait for everyone to finish
comm.barrier()
MPI.Finalize()

