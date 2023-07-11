library(utils)
options(timeout=36000)
options(repos = c(CRAN = "https://cloud.r-project.org"))
options(download.file.method = "libcurl", download.file.extra = "--no-check-certificate")


if (!require("BiocManager", quietly=TRUE))
    install.packages("BiocManager")

if (!require(devtools)) install.packages("devtools")

# MutationalPatterns
install.packages("vctrs")
BiocManager::install("NMF", update=FALSE)
install.packages("ggdendro")
install.packages("cowplot")
install.packages("ggalluvial")
BiocManager::install("MutationalPatterns", update=FALSE)

# SignatureToolsLib
install.packages("processx")
install.packages("cli")
devtools::install_github("linxihui/NNLM", upgrade="never")
devtools::install_github("Nik-Zainal-Group/signature.tools.lib", upgrade="never")

# Sigminer
BiocManager::install("sigminer", dependencies=TRUE, update=FALSE)

# SigFit
#devtools::install_github("kgori/sigfit", build_vignettes=TRUE, build_opts=c("--no-resave-data", "--no-manual"), upgrade="never")

# MutSignatures
install.packages("mutSignatures")
