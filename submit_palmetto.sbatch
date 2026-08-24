#!/bin/bash
#SBATCH --job-name=snIa_bremsstrahlung
#SBATCH --partition=work1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --mem=16G
#SBATCH --time=06:00:00
#SBATCH --mail-type=ALL
set -e

cd /scratch/cdipasq/AstrophysicsResearch

module load gcc/12.3.0
module load spack
spack load geant4@11.2.2
# cmake and python3 are plain system binaries (/usr/bin) on Palmetto, no
# module/spack load needed for those.

chmod +x run_batch.sh
./run_batch.sh

echo Done