# Two Percent Sprint Data Challenge

Simulating 2% of the DESI survey

## Simulated Observations

1. Install version 0.4.0 of the `desisurvey` and `surveysim` packages, e.g.:
```
cd /tmp
git clone git@github.com:desihub/desisurvey.git
cd desisurvey
git checkout 0.4.0
python setup.py develop
```
The `develop` option is required since the file `data/tiles-info.fits` is not copied by the install.  Note that the python version `desisurvey 0.3.1.dev1` does not match the tag.

```
cd /tmp
git clone git@github.com:desihub/surveysim.git
cd surveysim
git checkout 8e796cd
python setup.py install
```
We use the commit `8e796cd` right after the 0.4.0 tag since it provides an necessary bug fix. Note that the python version `surveysim 0.3.1.dev93` does not match the tag.

2. Simulate the first year of observations using the cmd-line script:
```
cd /tmp
mkdir work
cd work
% surveysim --start 2019-08-28 --stop 2020-07-13 --seed 123
```

3. Select the ? tiles observed in the first 35 nights from the list of all observed tiles with:
```
import astropy.table
def get_twopct(start='2019-08-28', stop='2019-10-01'):
    # Read all simulated observations.
    t = astropy.table.Table.read('obslist_all.fits')
    # Select the two-percent subsample based on MJD.
    start = astropy.time.Time(start)
    stop = astropy.time.Time(stop)
    num_nights = stop.mjd - start.mjd + 1
    sel = (t['STATUS'] > 0) & (t['MJD']>= start.mjd) & (t['MJD'] <= stop.mjd)
    t = t[sel]
    for pass_num in range(8):
        print('Observed {0:7d} tiles from PASS {1}'
              .format(len(t[t['PASS'] == pass_num]), pass_num))
    print('Observed {0:7d} tiles total during {1} nights'.format(len(t), num_nights))
    # Write selected columns to an ECSV file.
    t = t[['MJD', 'EXPTIME', 'PROGRAM', 'PASS', 'TILEID', 'RA', 'DEC',
           'MOONFRAC', 'MOONDIST', 'MOONALT', 'SEEING', 'AIRMASS']]
    t.meta['START'] = str(start.datetime.date())
    t.meta['STOP'] = str(stop.datetime.date())
    t.write('twopct.ecsv', format='ascii.ecsv')
```
Summary statistics for this sample:
```
Observed     152 tiles from PASS 0
Observed      14 tiles from PASS 1
Observed       2 tiles from PASS 2
Observed       1 tiles from PASS 3
Observed      44 tiles from PASS 4
Observed     122 tiles from PASS 5
Observed       4 tiles from PASS 6
Observed       1 tiles from PASS 7
Observed     340 tiles total during 35.0 nights
```
