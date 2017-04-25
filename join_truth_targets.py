#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
from mpi4py import MPI

import os, sys, glob, time

import numpy as np
import fitsio

def merge_table_data(infiles, ext=1):
    '''
    Merge the tables in HDU 1 of a set of input files
    '''
    data = [fitsio.read(x, ext) for x in infiles]
    return np.hstack(data)

def merge_files(comm, globname, ext, outfile):
    size = comm.Get_size()
    rank = comm.Get_rank()
    if rank == 0:
        infiles = glob.glob(globname)
        print('Merging {} files from {}'.format(len(infiles), globname))
        sys.stdout.flush()
    else:
        infiles = None

    infiles = comm.bcast(infiles, root=0)

    #- Each rank reads and combines a different set of files
    if rank == 0:
        print('reading', time.asctime())

    data = merge_table_data(infiles[rank::size], ext=ext)

    if rank == 0:
        print('gathering', time.asctime())

    data_tables = comm.gather(data, root=0)
        
    #- Recombine and stack at rank 0
    if rank == 0:
        print('stacking', time.asctime())
        data = np.hstack(data_tables)

    if rank == 0:
        print('writing {}'.format(outfile), time.asctime())
        sys.stdout.flush()
        header = fitsio.read_header(infiles[0], ext)
        tmpout = outfile + '.tmp'
        fitsio.write(tmpout, data, header=header)
        os.rename(tmpout, outfile)

#-------------------------------------------------------------------------
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

import optparse

parser = optparse.OptionParser(usage = "%prog [options]")
parser.add_option("-i", "--indir", type=str,  help="input directory")
parser.add_option("-o", "--outdir", type=str,  help="output directory")
# parser.add_option("-v", "--verbose", action="store_true", help="some flag")

opts, args = parser.parse_args()

#- Edison defaults for debugging convenience
if opts.indir is None:
    opts.indir = '/global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI'

if opts.outdir is None:
    opts.outdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets'

#- Cori
# if opts.indir is None:
#     opts.indir = '/global/cscratch1/sd/sjbailey/desi/dc17a/scratch/'
# if opts.outdir is None:
#     opts.outdir = '/global/cscratch1/sd/sjbailey/desi/dc17a/targets/'

#- Check which outputs still need to be done (in case we had to rerun)
if rank == 0:
    todo = dict()
    todo['sky'] = not os.path.exists(opts.outdir+'/sky.fits')
    todo['std_dark'] = not os.path.exists(opts.outdir+'/standards-dark.fits')
    todo['std_bright'] = not os.path.exists(opts.outdir+'/standards-bright.fits')
    todo['targets'] = not os.path.exists(opts.outdir+'/targets.fits')
    todo['truth'] = not os.path.exists(opts.outdir+'/truth.fits')
else:
    todo = None

todo = comm.bcast(todo, root=0)

if todo['sky']:
    merge_files(comm, opts.indir+'/output_*/sky.fits', 1, opts.outdir+'/sky.fits')

if todo['std_dark']:
    merge_files(comm, opts.indir+'/output_*/standards-dark.fits', 1, opts.outdir+'/standards-dark.fits')

if todo['std_bright']:
    merge_files(comm, opts.indir+'/output_*/standards-bright.fits', 1, opts.outdir+'/standards-bright.fits')

if todo['targets']:
    merge_files(comm, opts.indir+'/output_*/???/targets-*.fits', 1, opts.outdir+'/targets.fits')

if todo['truth']:
    merge_files(comm, opts.indir+'/output_*/???/truth-*.fits', 'TRUTH', opts.outdir+'/truth.fits')

MPI.Finalize()

#- MTL (maybe not bother in a parallel job while other cores sit idle?)
# if rank == 0:
#     out_mtl = os.path.join(outdir,'mtl.fits')
#     if not os.path.exists(out_mtl):
#         from desitarget import mtl
#         targets = fitsio.read(outdir+'/targets.fits')
#         mtl = mtl.make_mtl(targets)
#         tmpout = out_mtl+'.tmp'
#         fitsio.write(tmpout, mtl)
#         os.rename(tmpout, out_mtl)





