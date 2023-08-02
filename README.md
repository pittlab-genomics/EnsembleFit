# EnsembleFit
A method for mutational signature assignment through ensemble approaches

## Get Started (Docker)

1. Pull EnsembleFit latest Docker image.

```
docker pull pittgenomics/ensemblefit:latest
```

2. Run the container with sample data.

```
```

## Get Started (Non-Docker)

Requirements:
- Anaconda or Miniconda with Python 3
- Linux or Windows Subsystem for Linux (WSL)
- Estimated 12 GB of free storage

1. Clone this repository and change to the directory

```
git clone https://github.com/pittlab-genomics/EnsembleFit
cd EnsembleFit
```

2. Install Conda environment and dependencies. WARNING: This step may take 2-4 hours depending on your system to download and install all tools and their dependencies. 
```
bash setup/install_assignment_env.sh
```

3. Activate the `ensemblefit` conda environment and choose the reference genome version to install (E.g. GRCh37, GRCh38). In this example, GRCh37 is installed.
```
conda activate ensemblefit
python setup/install_genome.py GRCh37
```

4. Modify (or leave as default) the configuration file `assignment_config.json` and run the workflow.

```
python src/assignment.py
```

## Assignment configuration explained

The configuration file `assignment_config.json` is parsed by the main workflow to obtain all necessary paths and parameters.


| Key  | Value | Description |
| ------------- | ------------- | ------------- |
| `file_type`  | `txt`/`vcf`  | The file type of the input samples; either variant calls (vcf) or the SBS96 mutational catalogue (txt). |
| `genome_reference`  | `GRCh37`/`GRCh38`/`mm9`/`mm10`/`mm39`  | Reference genome used to align and call the variants for the samples. |
| `samples` | `PATH_TO_SAMPLES` | The path to the samples from current working directory. If samples are VCF, set path to the directory containing all the VCF files. If samples are mutational catalogue, set path to the mutational catalogue itself. |
| `signature_reference` | `PATH_TO_REFERENCE` | The reference signature set (e.g. COSMIC), users can select their own or from this repository in `signature_reference/` directory. |
| `output` | `PATH_TO_OUTPUT` | The output to store all results. Two directories will be created by the workflow: `PATH_TO_OUTPUT/temp` and `PATH_TO_OUTPUT/results`. |
| `strategy` | `regular`/`remove`/`refit` | The assignment strategy to be used by all tools. |
| `tools` | `{Tool: true/false}` | The selection of which tools to be included in the analysis. The ensemble result depends on the choice of tools. | 


## Build and Publish Docker Images

1. Build base Docker image.

```
docker build -t pittgenomics/ensemblefit:base -f Dockerfile.base .
docker push pittgenomics/ensemblefit:base
```

2. Build EnsembleFit Docker image.

```
docker build -t pittgenomics/ensemblefit:latest -f Dockerfile .
docker push pittgenomics/ensemblefit:latest
```
