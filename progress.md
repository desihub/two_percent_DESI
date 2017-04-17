# Progress Towards Completing the 2% Sprint

## Dataflow Overview

| Script              | Inputs              | Ouptuts        |  NJobs | Time/job | Status     |
|---------------------|---------------------|----------------|--------|----------|------------|
| surveysim           | footprint           | twopct.ecsv    |      1 |     4min | done       |
| select_mock_targets | mock catalogs       | target catalog | 1/sqdeg |         |            |
| newexp-desi         | twopct.ecsv         | simspecs       |  1/exp |          |            |
| quickgen            | fibermaps, simspecs | frames         |  1/exp |          |            |
| pipeline-fiberflat  | flat frames         | fiberflat      | 1/flat |          |            |
| pipeline-sky        | frames, fiberflats  | sky models     |  1/exp |          |            |
| pipeline-stdstars   | frames, fiberflats, sky | stdstars   |  1/exp |          |            |
| pipeline-fluxcal    | frames, fiberflats, sky model, stdstars | calib | 1/exp | | |
| pipeline-calibrate  | frames, fiberflats, sky, calib | cframes | 1/exp | | |
| pipeline-bricks     | cframes             | bricks         | 1/exp | | |
| pipeline-redshift   | bricks              | zbest          | 1/exp | | |

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

### Spectra + Observing Conditions to Frames

### Pipeline: Frames to Bricks

### Pipeline: Redshift Fitting
