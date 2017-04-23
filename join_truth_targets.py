#!/usr/bin/env python
from desitarget import mtl
import fitsio
import os
import desitarget.io as dtio
from astropy.table import Table, vstack
import glob
from argparse import ArgumentParser
import fitsio
import numpy as np
from astropy.io import fits

spec_out = False

dest_dir = 'final_output'
out_targets = os.path.join(dest_dir,'targets.fits')
out_truth = os.path.join(dest_dir,'truth.fits')
out_mtl = os.path.join(dest_dir,'mtl.fits')


out_spectra = os.path.join(dest_dir, 'spectra.fits')
if os.path.isfile(out_spectra):
    os.remove(out_spectra)

alltruth = []
alltargets = []

dirs = glob.glob("output_*")
for d in dirs:
    iter_truth = dtio.iter_files(d, 'truth')
    iter_target = dtio.iter_files(d, 'targets')
    for truth_file, target_file in zip(iter_truth, iter_target):
        alltruth.append(Table.read(truth_file))
        alltargets.append(Table.read(target_file))

        if spec_out:
            spec = fitsio.FITS(truth_file)
            fitsio.write(out_spectra, spec[1][:,:].astype(np.float32))

        print(truth_file, target_file)

targets = vstack(alltargets)
truth = vstack(alltruth)
mtl = mtl.make_mtl(targets)

targets.write(out_targets, overwrite=True)
truth.write(out_truth, overwrite=True)
mtl.write(out_mtl, overwrite=True)





