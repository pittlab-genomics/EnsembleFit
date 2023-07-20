#!/bin/bash
set -e

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh
CONDA_ENV_NAME="ensemblefit"

if conda env list | awk '{print $1}' | grep -Eq "^${CONDA_ENV_NAME}$"; then
  echo "######## Conda environment found: $CONDA_ENV_NAME"
  conda activate $CONDA_ENV_NAME
else
  echo "######## Conda environment not found, creating: $CONDA_ENV_NAME"
  #conda env create -n $CONDA_ENV_NAME --file ./setup/environment.yml
  conda create -y -n $CONDA_ENV_NAME python=3.9
  conda activate $CONDA_ENV_NAME

# Install conda packages using `conda install` (for first use only)
  conda install -y -c bioconda -c anaconda -c r -c conda-forge r=4.2 r-essentials=4.2 r-devtools=2.4.3 r-ggplot2=3.3.6 cmake=3.22.1 setuptools=65.6.3 wheel=0.38.4 r-xml r-rcpparmadillo r-gmp r-processx lapack
  pip install boto3==1.26.109 parsl==2023.4.17 awslambdaric==2.0.4 sigprofilerassignment==0.0.29
fi

# R-based tools
Rscript setup/install_rtools.R

echo "######## Update environment based on following output #######"
conda env export --no-builds

echo "######## Set up complete, environment name is: $CONDA_ENV_NAME ########"
