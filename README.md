# two percent of DESI observations

This repo has files related to the 2017 data challenges of processing
2% of DESI observations.

## dc17a ##

Spring 2017.

The original "2% sprint" that turned out to take quite awhile.
We succeeded at processing 2%, but not in a clean, easy, documented,
and reproducible way.

## mini ##

Summer 2017.

Post-dc17a, establishing the steps for processing just 5 tiles end-to-end
and fixing dataflow issues along the way.  It turns out that 2% of DESI
is an unwieldy amount of data for testing.  Even 5 tiles = 25k spectra isn't
trivial.

## dc17b ##

Not started yet.  This will be a redo of dc17a, using what we learned/fixed
from the dc17a and the mini-sprint to redo 2% of DESI with the latest code
in a more streamlined and documented manner.

## Future ##

### 2% to full-depth ###

dc17a and dc17b are 2% of observations, which cover more than 2% of the area
but to only a single layer of depth.  We could also do a test with 2% of the
area to full depth, which would be especially useful for Lyman-alpha studies.

### 2% with raw data ###

Do this including pixel-level simulations + extractions instead of
spectral-level simulations.

### Scaling up ###

Then onwards to 5%, 20%, 100%...

