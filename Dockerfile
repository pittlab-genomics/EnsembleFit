FROM pittgenomics/ensemblefit:base

SHELL ["/bin/bash", "--login", "-c"]

COPY . /app

CMD ["src/assignment.py"]
