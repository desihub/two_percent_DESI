# Progress Towards Completing the 2% Sprint

## Dataflow Overview

(specsim version, not pixsim version)

| Script              | Inputs              | Ouptuts        |  NJobs | Time | Status     |
|---------------------|---------------------|----------------|--------|----------|------------|
| surveysim           | footprint           | twopct.ecsv    |      1 |     4min | done       |
| select_mock_targets | mock catalogs       | target catalog, mock spectra | 1/sqdeg |    15min/job, but lots of human time     | done |
| fiberassign         | target catalog      | fiber assignments | 1 | <10min | done |
| newexp-desi         | twopct.ecsv, target catalog, mock spectra, fiberassign | simspecs, fibermaps |  1/night (?) | ~7min/exp |  refactoring |
| quickgen            | fibermaps, simspecs | frames         |  1/exp | >30min/exp | streamlining as fastframe |
| pipeline-fiberflat  | flat frames         | fiberflat      | 1/night |   | ready |
| pipeline-sky        | frames, fiberflats  | sky models     |  1/night |          | ready |
| pipeline-stdstars   | frames, fiberflats, sky | stdstars   |  1/night |          | ready |
| pipeline-fluxcal    | frames, fiberflats, sky model, stdstars | calib | 1/night | | ready |
| pipeline-calibrate  | frames, fiberflats, sky, calib | cframes | 1/night | ~10min/exp ff,sky,std,calib| ready |
| pipeline-bricks     | cframes             | bricks         | 1/night | | refactoring for scaling |
| pipeline-redshift   | bricks              | zbest          | 1/night | <10min/250spec | refactoring |

Status notes:
- done = already run for 2% survey
- refactoring = actively changing code, not yet ready to run even if inputs are ready
- ready = code is tested and ready to run, awaiting inputs

References:
- surveysim recipe is [here](README.md)
- select_mock_targets code is [here](https://github.com/desihub/desitarget/blob/master/bin/select_mock_targets)
- newexp-desi code is [here](https://github.com/desihub/desisim/blob/master/bin/newexp-desi)
- quickgen documented in code header [here](https://github.com/desihub/desisim/blob/master/py/desisim/scripts/quickgen.py)
- Pipeline processing steps are documented [here](https://github.com/desihub/desispec/blob/master/doc/pipeline.rst)

## Details on Individual Steps

For each step:
1. List shortcuts taken for the 2% sprint that should be revisited before the 20% milestone.
2. Mention any missing functionality that should be implemented before the 20% milestone.
3. Describe bottlenecks that need to be sped up before running 20% jobs.

### Simulate Observing Conditions & Schedule Tiles

1. Recipe to simulate observations was not reproducible.
2. Scheduling algorithm and its implementation (afternoon plan + next-field-sel) need more vetting & docs.
3. No performance issues.

### Tiles to Spectra
1. The reuse of `select_mock_targets` in a non-optimal way to generate all the data. (Details. This [python script](https://github.com/desihub/two_percent_DESI/blob/master/sprint.py) is the driver to generate targets+truth+spectra for chuncks of a few square degrees. It takes as an input the scheduled set of tiles. This [python script](https://github.com/desihub/two_percent_DESI/blob/master/write_slurm_targets.py) generates the  slurm script file. The outputs are in separate directories and files that need to be glued.)
2. Target generation needs to be MPI parallel. The final output directory structure should have less directories and files. See the checklist [here](https://github.com/desihub/desitarget/issues/169#issuecomment-296156292).
3. A MPI parallel version.

### Targets, Spectra, Observing Conditions, Fiber Assignments to simspec

1. Refactor in progress in desisim newexp branch.
2. Skipping galsim; need object shapes from input targets or fixed GMM installation in desitarget.
3. Performance seems ok but needs parallelism wrappers

### quickgen: simspec to frames

1/2. does not use specsim fiberloss calculations or per-fiber flatlamp spectra
3. quickgen>30 min per exposure; simplifying functionality as "fastframe" to streamline just simspec -> frames; needs multi-exposure parallelism wrapper

### pixsim+extract: simspec to frames

1. Currently skipping; using quickgen instead

### Pipeline: frames to cframes (flux calibrated frames)

Needs missing flat lamp frames from quickgen (fastframe will provide) but otherwise handoff has been tested and is fast and parallelized.

TODO: add S/N per band and propagate forward to zbest files

### Pipeline: cframes to bricks

May be viable for 2%; needs parallelism refactor to scale to 20% to avoid opening and closing N>>1 files M>>1 times.
Reorganize as healpix grouping.  Ted is working on this.

### Pipeline: Redshift Fitting

desispec branch `rrdesi` lays groundwork for using redrock instead of redmonster.
Still needs some batch job updates for running one MPI rank per brick per node.
Redrock still at https://github.com/sbailey/redrock; needs to move to desihub.
Redrock does ~125 targets/minute on 1 Cori node (32 cores); scaling depends on
number of targets per file (more is better).

z<2 QSOs have poor results, need to debug why.

### Misc

1. Review and update datamodel prior to 20% run
