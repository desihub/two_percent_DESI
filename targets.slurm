#!/bin/bash -l
#SBATCH -p regular
#SBATCH -N 46
#SBATCH -t 10:00:00
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
srun -N 1 -n 1 -c 32  sprint.py --first 0 --last 30 &
srun -N 1 -n 1 -c 32  sprint.py --first 30 --last 60 &
srun -N 1 -n 1 -c 32  sprint.py --first 60 --last 90 &
srun -N 1 -n 1 -c 32  sprint.py --first 90 --last 120 &
srun -N 1 -n 1 -c 32  sprint.py --first 120 --last 150 &
srun -N 1 -n 1 -c 32  sprint.py --first 150 --last 180 &
srun -N 1 -n 1 -c 32  sprint.py --first 180 --last 210 &
srun -N 1 -n 1 -c 32  sprint.py --first 210 --last 240 &
srun -N 1 -n 1 -c 32  sprint.py --first 240 --last 270 &
srun -N 1 -n 1 -c 32  sprint.py --first 270 --last 300 &
srun -N 1 -n 1 -c 32  sprint.py --first 300 --last 330 &
srun -N 1 -n 1 -c 32  sprint.py --first 330 --last 360 &
srun -N 1 -n 1 -c 32  sprint.py --first 360 --last 390 &
srun -N 1 -n 1 -c 32  sprint.py --first 390 --last 420 &
srun -N 1 -n 1 -c 32  sprint.py --first 420 --last 450 &
srun -N 1 -n 1 -c 32  sprint.py --first 450 --last 480 &
srun -N 1 -n 1 -c 32  sprint.py --first 480 --last 510 &
srun -N 1 -n 1 -c 32  sprint.py --first 510 --last 540 &
srun -N 1 -n 1 -c 32  sprint.py --first 540 --last 570 &
srun -N 1 -n 1 -c 32  sprint.py --first 570 --last 600 &
srun -N 1 -n 1 -c 32  sprint.py --first 600 --last 630 &
srun -N 1 -n 1 -c 32  sprint.py --first 630 --last 660 &
srun -N 1 -n 1 -c 32  sprint.py --first 660 --last 690 &
srun -N 1 -n 1 -c 32  sprint.py --first 690 --last 720 &
srun -N 1 -n 1 -c 32  sprint.py --first 720 --last 750 &
srun -N 1 -n 1 -c 32  sprint.py --first 750 --last 780 &
srun -N 1 -n 1 -c 32  sprint.py --first 780 --last 810 &
srun -N 1 -n 1 -c 32  sprint.py --first 810 --last 840 &
srun -N 1 -n 1 -c 32  sprint.py --first 840 --last 870 &
srun -N 1 -n 1 -c 32  sprint.py --first 870 --last 900 &
srun -N 1 -n 1 -c 32  sprint.py --first 900 --last 930 &
srun -N 1 -n 1 -c 32  sprint.py --first 930 --last 960 &
srun -N 1 -n 1 -c 32  sprint.py --first 960 --last 990 &
srun -N 1 -n 1 -c 32  sprint.py --first 990 --last 1020 &
srun -N 1 -n 1 -c 32  sprint.py --first 1020 --last 1050 &
srun -N 1 -n 1 -c 32  sprint.py --first 1050 --last 1080 &
srun -N 1 -n 1 -c 32  sprint.py --first 1080 --last 1110 &
srun -N 1 -n 1 -c 32  sprint.py --first 1110 --last 1140 &
srun -N 1 -n 1 -c 32  sprint.py --first 1140 --last 1170 &
srun -N 1 -n 1 -c 32  sprint.py --first 1170 --last 1200 &
srun -N 1 -n 1 -c 32  sprint.py --first 1200 --last 1230 &
srun -N 1 -n 1 -c 32  sprint.py --first 1230 --last 1260 &
srun -N 1 -n 1 -c 32  sprint.py --first 1260 --last 1290 &
srun -N 1 -n 1 -c 32  sprint.py --first 1290 --last 1320 &
srun -N 1 -n 1 -c 32  sprint.py --first 1320 --last 1350 &
srun -N 1 -n 1 -c 32  sprint.py --first 1350 --last 1380 &
wait
