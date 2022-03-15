#!/bin/bash -l
#SBATCH --time=24:00:00
#SBATCH --ntasks=24
#SBATCH --mem=72g
#SBATCH --mail-type=END,FAIL     # Mail events (can use any combination of the following: ALL, NONE, BEGIN, END, FAIL)
#SBATCH --mail-user=hassa601@umn.edu
#SBATCH -p amdsmall

export PATH=/home/srivasta/hassa601/
export PATH=/home/srivasta/hassa601/.conda/envs/myenv/bin:$PATH
python -u ethnicity_pipeline_MSI.py
