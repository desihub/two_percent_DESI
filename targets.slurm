!/bin/bash -l

#SBATCH  -p regular
#SBATCH -N 1
#SBATCH -t 1:00:00
#SBATCH -L SCRATCH,project

cd $SLURM_SUBMIT_DIR
echo "# Running "
srun -N 1 -n 1 -c 24 python sprint.py
