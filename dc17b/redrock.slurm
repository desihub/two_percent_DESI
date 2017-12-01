#!/bin/bash -l

#SBATCH --partition=regular
#SBATCH --constraint=haswell
#SBATCH --account=desi
#SBATCH --nodes=100
#SBATCH --time=00:40:00
#SBATCH --job-name=redrock

echo Starting slurm script at `date`

source /project/projectdirs/desi/software/desi_environment.sh master
source $SCRATCH/desi/dc17b/spectro/redux/dc17b/setup.sh
module swap redrock/sjb

export NODES=$SLURM_JOB_NUM_NODES
time srun -N $NODES -n $NODES -c 64 ./wrap-redrock --reduxdir $DESI_SPECTRO_REDUX/$SPECPROD --mpi

