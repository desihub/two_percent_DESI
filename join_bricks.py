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

def mergetruth(infiles, targetids, outfile):
    if len(infiles) > 1:
        flux = np.vstack( [fitsio.read(x, 'FLUX') for x in infiles] )
        truth = np.hstack( [fitsio.read(x, 'TRUTH') for x in infiles] )
    else:
        flux = fitsio.read(infiles[0], 'FLUX')
        truth = fitsio.read(infiles[0], 'TRUTH')

    truth['TARGETID'] = targetids

    wave = fitsio.read(infiles[0], 'WAVE')
    wavehdr = fitsio.read_header(infiles[0], 'WAVE')
    fluxhdr = fitsio.read_header(infiles[0], 'FLUX')
    truthhdr = fitsio.read_header(infiles[0], 'TRUTH')

    outtmp = outfile + '.tmp'
    fitsio.write(outtmp, wave, extname='WAVE', header=wavehdr, clobber=True)
    fitsio.write(outtmp, flux, header=fluxhdr, extname='FLUX')
    fitsio.write(outtmp, truth, header=truthhdr, extname='TRUTH')
    os.rename(outtmp, outfile)

def mergetargets(infiles, outfile):
    '''
    Merge a set of partial-brick target files into a single target file.
    Reassigns TARGETIDs due to repeated IDs in original files.
    Returns array of new TARGETIDs
    '''
    if len(infiles) > 1:
        targets = np.hstack( [fitsio.read(x, 1) for x in infiles] )
    else:
        targets = fitsio.read(infiles[0], 1)

    header = fitsio.read_header(infiles[0])
    targets['TARGETID'] = np.random.randint(2**63, size=len(targets))

    outtmp = outfile + '.tmp'
    fitsio.write(outtmp, targets, header=header, extname='TARGETS', clobber=True)
    os.rename(outtmp, outfile)
    
    return targets['TARGETID'].copy()

#-------------------------------------------------------------------------
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

import optparse

parser = optparse.OptionParser(usage = "%prog [options]")
parser.add_option("-i", "--indir", type=str,  help="input directory")
parser.add_option("-o", "--outdir", type=str,  help="output directory")

opts, args = parser.parse_args()

#- Set a different seed for each rank, but based on a common seed
np.random.seed(1)
seeds = np.random.randint(2**31, size=size)
np.random.seed(seeds[rank])

#- Edison defaults for debugging convenience
if opts.indir is None:
    opts.indir = '/global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI'

if opts.outdir is None:
    opts.outdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets/'

#- Build dictionary of files associated with each brickname;
#- use rank 0 only to not overwhelm disk
if rank == 0:
    print('Scanning input target files', time.asctime())
    targetfiles = glob(opts.indir+'/output_*/???/targets-*.fits')

    bricks = dict()
    for filename in targetfiles:
        brickname = os.path.basename(filename)[8:16]
        if brickname not in bricks:
            bricks[brickname] = [filename, ]
        else:
            bricks[brickname].append(filename)
else:
    bricks = None

#- Broadcast brick dictionary to all ranks
comm.barrier()
bricks = comm.bcast(bricks, root=0)
bricknames = sorted(bricks.keys())

#- Create output subdirectories using rank 0 process
if rank == 0:
    print('Creating subdirs for {} bricks'.format(len(bricknames)))
    for prefix in set([b[0:3] for b in bricknames]):
        subdir = os.path.join(opts.outdir, prefix)
        if not os.path.exists(subdir):
            os.mkdir(subdir)

#- Wait for rank 0 to finish making directories
comm.barrier()

#- For testing
# bricknames = bricknames[0:size*4]

#- Start processing bricks
for i in range(rank, len(bricknames), size):
    brickname = bricknames[i]
    subdir = os.path.join(opts.outdir, brickname[0:3])

    print('Rank {:3d}: {}/{} brickname {}'.format(rank, i, len(bricknames), bricknames[i]))
    sys.stdout.flush()

    targetfiles = bricks[brickname]
    outtargets = os.path.join(subdir, 'targets-{}.fits'.format(brickname)) 
    outtruth = os.path.join(subdir, 'truth-{}.fits'.format(brickname)) 

    if not os.path.exists(outtargets) or not os.path.exists(outtruth):
        targetids = mergetargets(targetfiles, outtargets)
        truthfiles = [x.replace('/targets-', '/truth-') for x in targetfiles]        
        mergetruth(truthfiles, targetids, outtruth)

#- Wait for everyone to finish
comm.barrier()
MPI.Finalize()

