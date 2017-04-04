# two_percent_DESI
Simulating 2% of the DESI survey

## Simulated Observations

1. Install `desisurvey v0.4.0` and `surveysim v0.4.0` then simulate the first year of observations using the cmd-line script:
```
% surveysim --start 2019-08-28 --stop 2020-07-13
```

2. Select the first 45 days from the list of all observed tiles using the following python function:
```
def get_twopct(start='2019-08-23', stop='2019-10-06'):
    # Read all simulated observations.
    t = astropy.table.Table.read('obslist_all.fits')
    # Select the two-percent subsample based on MJD.
    start = astropy.time.Time(start)
    stop = astropy.time.Time(stop)
    sel = (t['STATUS'] > 0) & (t['MJD']>= start.mjd) & (t['MJD'] <= stop.mjd)
    t = t[sel]
    # Write selected columns to an ECSV file.
    t = t[['MJD', 'EXPTIME', 'PROGRAM', 'PASS', 'TILEID', 'RA', 'DEC',
           'MOONFRAC', 'MOONDIST', 'MOONALT', 'SEEING', 'AIRMASS']]
    t.meta['START'] = str(start.datetime.date())
    t.meta['STOP'] = str(stop.datetime.date())
    t.write('twopct.ecsv', format='ascii.ecsv')
```
Summary statistics for this sample:
```
Observed     184 tiles with     0 repeats from PASS 0
Observed      13 tiles with     0 repeats from PASS 1
Observed       0 tiles with     0 repeats from PASS 2
Observed       0 tiles with     0 repeats from PASS 3
Observed      51 tiles with     0 repeats from PASS 4
Observed      63 tiles with     0 repeats from PASS 5
Observed       2 tiles with     0 repeats from PASS 6
Observed       0 tiles with     0 repeats from PASS 7
Observed     313 tiles with     0 repeats total.
```
