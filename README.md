# EnsembleFit
A method for mutational signature assignment through ensemble approaches

## Get Started

1. Pull EnsembleFit latest Docker image.

```
docker pull pittgenomics/ensemblefit:latest
```

2. Run the container with sample data.

```
```


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
