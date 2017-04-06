#!/bin/bash -l

#SBATCH  -p regular
#SBATCH -N 10
#SBATCH -t 12:00:00
#SBATCH -L SCRATCH,project
#SBATCH -J targets

cd $SLURM_SUBMIT_DIR
echo "# Running "
srun -N 1 -n 1 -c 24 python sprint.py --first 0 --last 5
srun -N 1 -n 1 -c 24 python sprint.py --first 5 --last 10
srun -N 1 -n 1 -c 24 python sprint.py --first 10 --last 15
srun -N 1 -n 1 -c 24 python sprint.py --first 15 --last 20
srun -N 1 -n 1 -c 24 python sprint.py --first 20 --last 25
srun -N 1 -n 1 -c 24 python sprint.py --first 25 --last 30
srun -N 1 -n 1 -c 24 python sprint.py --first 30 --last 35
srun -N 1 -n 1 -c 24 python sprint.py --first 35 --last 40
srun -N 1 -n 1 -c 24 python sprint.py --first 40 --last 45
srun -N 1 -n 1 -c 24 python sprint.py --first 45 --last 50

