#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
from mpi4py import MPI

import os, sys, glob

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

    infiles = comm.bcast(infiles, root=0)

    #- Each rank reads and combines a different set of files
    data = merge_table_data(infiles[rank::size], ext=ext)
    
    #- Recombine and stack at rank 0
    data = np.hstack(comm.gather(data, root=0))

    if rank == 0:
        header = fitsio.read_reader(infiles[0], ext)
        tmpout = outfile + '.tmp'
        fitsio.write(tmpout, data, header=header)
        os.rename(tmpout, outfile)

#-------------------------------------------------------------------------
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

#- Edison
# indir = '/global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI'
# outdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets/'

#- Cori
indir = '/global/cscratch1/sd/sjbailey/desi/dc17a/scratch/'
outdir = '/global/cscratch1/sd/sjbailey/desi/dc17a/targets/'

if rank == 0:
    if not os.path.exists(outdir+'/sky.fits')
        merge_files(comm, indir+'/output_*/sky.fits', 1, outdir+'/sky.fits')

    if not os.path.exists(outdir+'/standards-dark.fits'):
        merge_files(comm, indir+'/output_*/standards-dark.fits', 1, outdir+'/standards-dark.fits')

    if not os.path.exists(outdir+'/standards-bright.fits'):
        merge_files(comm, indir+'/output_*/standards-bright.fits', 1, outdir+'/standards-bright.fits')

    if not os.path.exists(outdir+'/targets.fits'):
        merge_files(comm, indir+'/output_*/???/targets-*.fits', 1, outdir+'/targets.fits')

    if not os.path.exists(outdir+'/truth.fits'):
        merge_files(comm, indir+'/output_*/???/truth-*.fits', 'TRUTH', outdir+'/truth.fits')

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





