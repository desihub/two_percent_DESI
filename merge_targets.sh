#!/bin/bash
#SBATCH -N 20
#SBATCH -p debug
#SBATCH -J mergemocks
#SBATCH --mail-user=StephenBailey@lbl.gov
#SBATCH -t 00:30:00

#OpenMP settings:
export OMP_NUM_THREADS=2
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

#run the application:
cd $SCRATCH/desi/code/two_percent_DESI
srun -n 240 -c 4 ./join_truth_targets.py \
    --indir /global/project/projectdirs/desi/users/forero/datachallenge2017/two_percent_DESI \
        --outdir $SCRATCH/desi/dc17a/targets


