#!/bin/bash
#SBATCH --job-name=singularity_build
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32  # Adjust based on available resources
#SBATCH --mem=48G           # Adjust based on available resources
#SBATCH --time=01:00:00    # Adjust based on expected build time

module load singularity  # Load Singularity module if necessary

# Limit the number of threads to prevent exceeding process limits
export SINGULARITY_BUILD_NTHREADS=32
cd /scratch/h3752/mysif/
singularity pull fmriprep_24.1.1.sif docker://nipreps/fmriprep:24.1.1