# dc17b: two-percent of DESI in a more traceable form

Work in progress based on desimodules test-release intended for tag 17.11.

## basic setup

mkdir -p $SCRATCH/desi/dc17b/survey
mkdir -p $SCRATCH/desi/dc17b/targets
mkdir -p $SCRATCH/desi/dc17b/fiberassign
mkdir -p $SCRATCH/desi/dc17b/spectro/redux
mkdir -p $SCRATCH/desi/dc17b/spectro/sim

## surveysim

Using /global/cscratch1/sd/dkirkby/desi/output/depth_0m

## Write list of tiles covered in the first month of operations

desisurvey/0.10.10 and surveysim/0.9.0

```python
import desisurvey.progress
os.environ['DESISURVEY_OUTPUT'] = '/global/cscratch1/sd/dkirkby/desi/output/depth_0m'
p = desisurvey.progress.Progress('progress.fits')
explist = p.get_exposures()

#- Add arcs/flats and assign exposure ids
import surveysim.util
explist = surveysim.util.add_calibration_exposures(explist)

#- surveysim started Dec 1 2019; pick just Dec 2019 dates
ii = (explist['NIGHT'] < '20200101')
expfile = os.getenv('SCRATCH')+'/desi/dc17b/survey/exposures.fits'
explist[ii].write(expfile)

#- Get subset of tiles covered by those exposures
import desimodel.io
from astropy.table import Table
tiles = Table(desimodel.io.load_tiles())
jj = np.in1d(tiles['TILEID'], explist['TILEID'][ii])
tilefile = os.environ['SCRATCH']+'/desi/dc17b/targets/twopct-tiles.fits'
tiles[jj].write(tilefile)

#- Write separate tiles lists for fiberassign dark+gray and bright
isbright = (tiles['PROGRAM'] == 'BRIGHT')
isdark = (tiles['PROGRAM'] == 'DARK')
isgray = (tiles['PROGRAM'] == 'GRAY')
assert np.all(isbright | isdark | isgray)

def write_text_tiles(outfile, tiles):
    with open(outfile, 'w') as fx:
        for tileid in tiles['TILEID']:
            fx.write('{}\n'.format(tileid))

outfile = os.environ['SCRATCH']+'/desi/dc17b/fiberassign/bright-tiles.txt'
write_text_tiles(outfile, tiles[jj & isbright])
outfile = os.environ['SCRATCH']+'/desi/dc17b/fiberassign/darkgray-tiles.txt'
write_text_tiles(outfile, tiles[jj & (isdark | isgray)])
```

## mpi_select_mock_targets

Using desitarget/0.16.1 and desisim/0.22.0

```console
export NODES=50
salloc -A desi -N $NODES -t 04:00:00 -C haswell --qos interactive

basedir=$SCRATCH/desi/dc17b
cd $SCRATCH/desi/code/two_percent_DESI/dc17b
srun -N $NODES -n $NODES -c 32  mpi_select_mock_targets \
    --seed 1 --nproc 32 --nside 64 --npix 8 \
    --tiles $basedir/targets/twopct-tiles.fits \
    --config ./select-mock-targets.yaml \
    --output_dir $basedir/targets
```

4 hours should be sufficient, but if the job times out before finishing
all bricks just run again and it will pickup where it left off.
I lost my ssh connection after 3 hours and had to restart for dc17b.

## Merge mock target catalogs

```console
salloc -N 1 -t 1:0:0 -C haswell --qos interactive
srun -n 8 -c 8 join_mock_targets --mockdir $SCRATCH/desi/dc17b/targets --force --mpi
mkdir -p /project/projectdirs/desi/www/users/sjbailey/dc17b/targets/qa
run_target_qa $SCRATCH/desi/dc17b/targets/targets.fits /project/projectdirs/desi/www/users/$USER/dc17b/targets/qa
```

See https://portal.nersc.gov/project/desi/users/sjbailey/dc17b/targets/qa

TODO: check space padding before proceeding beyond this
--> fitsio pads (ugh) but astropy.io.fits crashes (bigger ugh)

## fiberassign

```
basedir=$SCRATCH/desi/dc17b
mkdir -p $basedir/fiberassign
cd $basedir/fiberassign
config-fiberassign \
    --mtl $basedir/targets/mtl.fits \
    --stdstars $basedir/targets/standards-dark.fits \
    --sky $basedir/targets/sky.fits \
    --surveytiles $basedir/fiberassign/darkgray-tiles.txt \
    --outdir $basedir/fiberassign/ \
    --config $basedir/fiberassign/faconfig-darkgray.txt 
config-fiberassign \
    --mtl $basedir/targets/mtl.fits \
    --stdstars $basedir/targets/standards-bright.fits \
    --sky $basedir/targets/sky.fits \
    --surveytiles $basedir/fiberassign/bright-tiles.txt \
    --outdir $basedir/fiberassign/ \
    --config $basedir/fiberassign/faconfig-bright.txt 

fiberassign $basedir/fiberassign/faconfig-darkgray.txt
fiberassign $basedir/fiberassign/faconfig-bright.txt
```

## wrap-newexp

This step will need to be updated once we have the intermediate step of
generating an exposures.fits file with pre-generated exposure IDs and
arc/flat assignments.

768 exposures on 16 nights -> 768 + 16*3 = 816 exposures + fast arcs

90 sec/exp * 816 / 3600 = 20.4 node hours

```
export NODES=48
salloc -A desi -N $NODES -C haswell -p regular -t 2:00:00 --qos interactive

export DESI_SPECTRO_SIM=$SCRATCH/desi/dc17b/spectro/sim
export DESI_SPECTRO_REDUX=$SCRATCH/desi/dc17b/spectro/redux
export PIXPROD=dc17b
export SPECPROD=dc17b

basedir=$SCRATCH/desi/dc17b
srun -N $NODES -n $NODES -c 64 wrap-newexp --mpi \
    --fiberassign $basedir/fiberassign \
    --mockdir $basedir/targets \
    --obslist $basedir/survey/exposures.fits \
    --tilefile $basedir/targets/twopct-tiles.fits
```

--> Fixed crash in SUCCESS print message; need new tag (0.22.1)

## wrap-fastframe

```
export NODES=48
salloc -A desi -N $NODES -C haswell -p regular -t 2:00:00 --qos interactive

export DESI_SPECTRO_SIM=$SCRATCH/desi/dc17b/spectro/sim
export DESI_SPECTRO_REDUX=$SCRATCH/desi/dc17b/spectro/redux
export PIXPROD=dc17b
export SPECPROD=dc17b

srun -N $NODES -n $NODES -c 64 wrap-fastframe --mpi
```

## spectro pipeline

```
export DESI_SPECTRO_SIM=$SCRATCH/desi/dc17b/spectro/sim
export DESI_SPECTRO_REDUX=$SCRATCH/desi/dc17b/spectro/redux
export PIXPROD=dc17b
export SPECPROD=dc17b
export DESI_SPECTRO_DATA=$DESI_SPECTRO_SIM/$PIXPROD

desi_pipe --nersc_host cori --nersc_queue debug --fakepix

ls $DESI_SPECTRO_REDUX/$SPECPROD/run/scripts/*/fiberflat*.slurm | xargs -n 1 sbatch
```

## spectra regrouping

Takes 65 minutes, not 30 minutes:
```
sbatch --mail-type=END --mail-user=StephenBailey@lbl.gov -t 1:30:00 \
    $DESI_SPECTRO_REDUX/$SPECPROD/run/scripts/spectra.slurm
```

Tile 4969 doesn't have any spectra.  Odd.

## run redrock

```
export NODES=50
salloc -A desi -N $NODES -C haswell -p regular -t 4:00:00 --qos interactive

source $SCRATCH/desi/dc17b/spectro/redux/dc17b/setup.sh

time srun -N $NODES -n $NODES -c 64 ./wrap-redrock --reduxdir $DESI_SPECTRO_REDUX/$SPECPROD --mpi
```

submit a followup job
```
sbatch -d afterany:8261664 --qos premium redrock.slurm
```

## Make combined redshift catalog

```
source $SCRATCH/desi/dc17b/spectro/redux/dc17b/setup.sh
cd $DESI_SPECTRO_REDUX/$SPECPROD
desi_zcatalog -i spectra-64 -o zcat-$SPECPROD.fits
```

Merge the original target file with the zcatalog
```
import os
from astropy.table import Table, join

targetfile = os.getenv('SCRATCH')+'/desi/dc17b/targets/targets.fits'
targets = Table.read(targetfile)
zcat = Table.read('zcat-dc17b.fits')

#- remove sky fibers not in original target catalog
ii = np.in1d(zcat['TARGETID'], targets['TARGETID'])
zcat = zcat[ii]

zcat.remove_column('BRICKNAME')
del zcat.meta['EXTNAME']
del targets.meta['EXTNAME']

ztarget = join(targets, zcat, keys='TARGETID', join_type='inner')

ztarget.meta['EXTNAME'] = 'ZTARGET'
ztarget.write('ztarget-dc17b.fits', overwrite=True)
```

## Redshift QA

QA is broken in master; doing this by hand.

```
from astropy.table import Table, join
zcat = Table.read('zcat-dc17b.fits')
truth = Table.read(os.getenv('SCRATCH')+'/desi/dc17b/targets/truth.fits')
ztruth = join(zcat, truth, keys='TARGETID')

#- Sigh
ztruth['TRUESPECTYPE'] = np.char.strip(ztruth['TRUESPECTYPE'])
ztruth['TEMPLATETYPE'] = np.char.strip(ztruth['TEMPLATETYPE'])
ztruth['SPECTYPE'] = np.char.strip(ztruth['SPECTYPE'])

isELG = (ztruth['TEMPLATETYPE'] == 'ELG')
isQSO = (ztruth['TEMPLATETYPE'] == 'QSO')
isLRG = (ztruth['TEMPLATETYPE'] == 'LRG')
isSTAR = (ztruth['TEMPLATETYPE'] == 'STAR')
isBGS = (ztruth['TEMPLATETYPE'] == 'BGS')
print('nQSO ', np.count_nonzero(isQSO))
print('nLRG ', np.count_nonzero(isLRG))
print('nELG ', np.count_nonzero(isELG))
print('nSTAR', np.count_nonzero(isSTAR))
print('nBGS ', np.count_nonzero(isBGS))

def zstats(zx, dvlimit=1000, count=False):
    dv = 1e5 * (zx['Z'] - zx['TRUEZ'])/(1+zx['TRUEZ'])
    good = (np.abs(dv)<=dvlimit) & (zx['ZWARN'] == 0)
    fail = (np.abs(dv)> dvlimit) & (zx['ZWARN'] == 0)
    miss = (np.abs(dv)<=dvlimit) & (zx['ZWARN'] != 0)
    lost = (np.abs(dv)> dvlimit) & (zx['ZWARN'] != 0)
    ngood = np.count_nonzero(good)
    nfail = np.count_nonzero(fail)
    nmiss = np.count_nonzero(miss)
    nlost = np.count_nonzero(lost)
    ntot = len(dv)
    assert(ntot == ngood+nfail+nmiss+nlost)
    if count:
        return ngood, nfail, nmiss, nlost
    elif ntot == 0:
        return (np.nan, np.nan, np.nan, np.nan)
    else:
        return 100*ngood/ntot, 100*nfail/ntot, 100*nmiss/ntot, 100*nlost/ntot

print('          ntarg   good  fail  miss  lost')
for objtype in set(ztruth['TEMPLATETYPE']):
    isx = (ztruth['TEMPLATETYPE'] == objtype)
    pgood, pfail, pmiss, plost = zstats(ztruth[isx])
    nx = np.count_nonzero(isx)
    print('{:6s} {:8d}  {:5.1f} {:5.1f} {:5.1f} {:5.1f}'.format(objtype, nx, pgood, pfail, pmiss, plost))

print()
print('good = correct redshift and ZWARN==0')
print('fail = bad redshift and ZWARN==0 (i.e. catastrophic failures)')
print('miss = correct redshift ZWARN!=0 (missed opportunities)')
print('lost = wrong redshift ZWARN!=0 (wrong but at least we know it)')
```

```
          ntarg   good  fail  miss  lost
LRG      305030  100.0   0.0   0.0   0.0
QSO      194319   96.4   0.8   1.9   0.9
WD         6846   89.2   7.3   0.7   2.8
BGS      889336   94.2   0.2   3.6   2.0
ELG      601847   88.4   0.5   5.1   5.9
STAR     134518   87.4   0.4   2.1  10.1
```

