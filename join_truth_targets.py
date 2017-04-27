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

def merge_files(comm, globname, ext, outfile, outextname=None):
    '''
    Doesn't work for large merges; pickle barfs if objects are too big
    '''
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
    # print('Rank {} got {} rows'.format(rank, len(data)))

    def tmpfile(outfile, rank):
        return '{}-{}'.format(outfile, rank)

    #- Merge via temporary files on disk (!) because the data tables are
    #- too big to be sent via pickle (comm.gather, comm.send) but the dtype
    #- is also too complex to be sent via the non-pickle methods (comm.Send)
    #- Ugly hack, but pragmatically this works well
    fitsio.write(tmpfile(outfile, rank), data, clobber=True)
    comm.barrier()

    if rank == 0:
        print('stacking', time.asctime())
        data_tables = list()
        for i in range(size):
            data_tables.append( fitsio.read(tmpfile(outfile, i), 1) )
            os.remove(tmpfile(outfile, i))
        data = np.hstack(data_tables)

    if rank == 0:
        print('writing {}'.format(outfile), time.asctime())
        sys.stdout.flush()
        header = fitsio.read_header(infiles[0], ext)
        tmpout = outfile + '.tmp'
        fitsio.write(tmpout, data, header=header, extname=outextname)
        os.rename(tmpout, outfile)
    
    comm.barrier()

#-------------------------------------------------------------------------
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

import optparse

parser = optparse.OptionParser(usage = "%prog [options]")
parser.add_option("-t", "--targetdir", type=str,  help="input targets directory")
parser.add_option("-s", "--skydir", type=str,  help="input sky directory")
parser.add_option("-o", "--outdir", type=str,  help="output directory")
# parser.add_option("-v", "--verbose", action="store_true", help="some flag")

opts, args = parser.parse_args()

#- Edison defaults for debugging convenience
if opts.skydir is None:
    opts.skydir = '/global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI'

if opts.targetdir is None:
    opts.targetdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets'

if opts.outdir is None:
    opts.outdir = '/scratch2/scratchdirs/sjbailey/desi/dc17a/targets/testmerge'

#- Cori
# if opts.indir is None:
#     opts.indir = '/global/cscratch1/sd/sjbailey/desi/dc17a/scratch/'
# if opts.outdir is None:
#     opts.outdir = '/global/cscratch1/sd/sjbailey/desi/dc17a/targets/'

out_sky = opts.outdir+'/sky.fits'
out_stddark = opts.outdir+'/standards-dark.fits'
out_stdbright = opts.outdir+'/standards-bright.fits'
out_targets = opts.outdir+'/targets.fits'
out_truth = opts.outdir+'/truth.fits'
out_mtl = opts.outdir+'/mtl.fits'

#- Check which outputs still need to be done (in case we had to rerun)
#- All ranks need to know this, but just ping the disk with rank 0
if rank == 0:
    todo = dict()
    todo['sky'] = not os.path.exists(out_sky)
    todo['targets'] = not os.path.exists(out_targets)
    todo['truth'] = not os.path.exists(out_truth)
else:
    todo = None

todo = comm.bcast(todo, root=0)

if todo['sky']:
    merge_files(comm, opts.skydir+'/output_*/sky.fits', 1, out_sky, 'SKY')

if todo['targets']:
    merge_files(comm, opts.targetdir+'/???/targets-*.fits', 1, out_targets, 'TARGETS')

if todo['truth']:
    merge_files(comm, opts.targetdir+'/???/truth-*.fits', 'TRUTH', out_truth, 'TRUTH')

#- Extracts standards from targets file we just wrote
#- These are fast enough that it is ok that the other ranks are idle
#- MTL is done last; writing it is the slowest
if rank == 0:
    if not os.path.exists(out_stddark) or \
       not os.path.exists(out_stdbright) or \
       not os.path.exists(out_mtl):
        import desitarget
        targets = fitsio.read(out_targets, 'TARGETS')

    if not os.path.exists(out_stddark):
        print('Generating '+out_stddark)
        isSTD = (targets['DESI_TARGET'] & desitarget.desi_mask['STD_FSTAR']) != 0
        tmpout = out_stddark + '.tmp'
        fitsio.write(tmpout, targets[isSTD], extname='STD')
        os.rename(tmpout, out_stddark)

    if not os.path.exists(out_stdbright):
        print('Generating '+out_stdbright)
        isSTD = (targets['DESI_TARGET'] & desitarget.desi_mask['STD_BRIGHT']) != 0
        tmpout = out_stdbright + '.tmp'
        fitsio.write(tmpout, targets[isSTD], extname='STD')
        os.rename(tmpout, out_stdbright)

    if not os.path.exists(out_mtl):
        print('Generating '+out_mtl)
        import desitarget.mtl
        mtl = desitarget.mtl.make_mtl(targets)
        tmpout = out_mtl+'.tmp'
        mtl.meta['EXTNAME'] = 'MTL'
        mtl.write(tmpout, format='fits')
        os.rename(tmpout, out_mtl)

MPI.Finalize()





