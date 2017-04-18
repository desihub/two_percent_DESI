#!/usr/bin/env python
from desitarget import mtl
import fitsio
import os
import desitarget.io as dtio
from astropy.table import Table, vstack

from argparse import ArgumentParser
ap = ArgumentParser()
ap.add_argument("-s", "--src", help="Tractor/sweeps file or root directory with tractor/sweeps files")
ap.add_argument("-d", "--dest", help="Output target selection file")
ns = ap.parse_args()

iter_truth = dtio.iter_files(ns.src, 'truth')
iter_target = dtio.iter_files(ns.src, 'targets')

alltruth = []
alltargets = []
for truth_file, target_file in zip(iter_truth, iter_target):
    alltruth.append(Table.read(truth_file))
    alltargets.append(Table.read(target_file))
    print(truth_file, target_file)

targets = vstack(alltargets)
truth = vstack(alltruth)
mtl = mtl.make_mtl(targets)

out_targets = os.path.join(ns.dest,'targets.fits')
out_truth = os.path.join(ns.dest,'truth.fits')
out_mtl = os.path.join(ns.dest,'mtl.fits')
targets.write(out_targets, overwrite=True)
truth.write(out_truth, overwrite=True)
mtl.write(out_mtl, overwrite=True)




