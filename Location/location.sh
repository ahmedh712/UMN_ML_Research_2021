#!/bin/bash -l
#SBATCH --time=90:00:00
#SBATCH --ntasks=2
#SBATCH --mem=64g
#SBATCH -p ram256g
#SBATCH --mail-type=END,FAIL # Mail events (can use any combination of the following: ALL, NONE, BEGIN, END, FAIL)
#SBATCH --mail-user=hassa601@umn.edu

module load python3
export PATH=/home/srivasta/hassa601/
export PATH=/home/srivasta/hassa601/.conda/envs/myenv/bin:$PATH
python -u location_pipeline_MSI.py