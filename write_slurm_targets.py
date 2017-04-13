import numpy as np
a = np.loadtxt('twopct.ecsv', skiprows=19, usecols=(4,5,6))
tileid= np.int_(a[:,0])
ra = a[:,1]
dec = a[:,2]

side_grid = 1.5
side_field = 1.5
n_tiles = len(a)
grid_list = []

for i in range(n_tiles):
    for k in [-1.0,0.0,1.0]:
        for l in [-1.0, 0.0, 1.0]:
            ra_corner = (ra[i] + k * side_field)%359.99
            dec_corner = (dec[i] + l * side_field)
            if dec_corner<-90.0:
                dec_corner = -90.0
            if dec_corner>90.0:
                dec_corner = -90.0

            ra_grid = int(ra_corner - ra_corner%side_grid)%359.99
            dec_grid = int(dec_corner - dec_corner%side_grid)
            if (ra_grid, dec_grid) not in grid_list:
                grid_list.append((ra_grid,dec_grid))

n_chunks = len(grid_list)
chunks_per_node = 30


n_nodes = n_chunks//chunks_per_node + 1
print(n_chunks, chunks_per_node, n_nodes)

fileout = open('targets.slurm', 'w')
fileout.write('#!/bin/bash -l\n')
fileout.write('#SBATCH -p regular\n')
fileout.write('#SBATCH -N {}\n'.format(n_nodes))
fileout.write('#SBATCH -t 10:00:00\n')
fileout.write('#SBATCH -L SCRATCH,project\n')
fileout.write('#SBATCH -C haswell\n')
 

for i in range(n_nodes):
    fileout.write('srun -N 1 -n 1 -c 32  sprint.py --first {} --last {}&\n'.format(i*chunks_per_node, (i+1)*chunks_per_node))

fileout.write('wait\n')
fileout.close()
