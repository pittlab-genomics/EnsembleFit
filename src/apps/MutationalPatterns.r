args <- commandArgs(trailingOnly=TRUE)
if (length(args) < 4) {
    stop("Need 4 arguments: sample_path reference_path output_path strategy", call.=FALSE)
}
sample_path <- args[1]
reference_path <- args[2]
output_path <- args[3]
strategy <- args[4]

if (!dir.exists(output_path)) {
    dir.create(output_path)
}

library(tidyverse)
library(tibble)
library(MutationalPatterns)

cat(paste0("[", Sys.time(), "] Start"), "\n")
##############################
# REGULAR
##############################
regular_fit <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))
    #matrix <- read.delim(sample_path, sep="\t")
    #matrix <- as.matrix(setNames(data.frame(t(matrix[,-1])), matrix[,1]))
    #matrix <- t(matrix)

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var = colnames(ref)[1])
    ref <- as.matrix(ref)

    regular <- fit_to_signatures(matrix, ref)
    regular <- t(regular$contribution)
    regular <- tibble::rownames_to_column(as.data.frame(regular), "Samples")

    write.table(regular, paste0(output_path, "/MutationalPatterns_regular.txt"), sep="\t", quote=FALSE, row.name=FALSE)
    cat(paste0("[", Sys.time(), "] Regular DONE"), "\n")
}
##############################
# REMOVE
##############################
strict_remove <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))
    total_mutations <- colSums(matrix)

    regular <- read.delim(paste0(output_path, "/MutationalPatterns_regular.txt"), sep="\t")
    remove <- regular
    unassigned <- c()
    for (i in 1:nrow(regular)) {
        new_row <- apply(regular[i, 2:ncol(regular)], 2, function(x) { ifelse(x < total_mutations[i] * 0.05, 0, x) })
        remove[i, 2:ncol(regular)] <- new_row
        unassigned <- c(unassigned, total_mutations[i] - sum(new_row))
    }
    remove$unassigned <- unassigned

    write.table(remove, paste0(output_path, "/MutationalPatterns_remove.txt"), sep="\t", quote=FALSE, row.name=FALSE)
    cat(paste0("[", Sys.time(), "] Remove DONE"), "\n")
}
##############################
# REFIT
##############################
strict_refit <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var = colnames(ref)[1])
    ref <- as.matrix(ref)

    refit <- fit_to_signatures_strict(matrix, ref)$fit_res
    refit <- t(refit$contribution)
    refit <- tibble::rownames_to_column(as.data.frame(refit), "Samples")

    write.table(refit, paste0(output_path, "/MutationalPatterns_refit.txt"), sep="\t", quote=FALSE, row.name=FALSE)
    cat(paste0("[", Sys.time(), "] Refit DONE"), "\n")
}
##############################
# MAIN
##############################
if (strategy == "all") {
    regular_fit()
    strict_remove()
    strict_refit()
} else if (strategy == "regular") {
    regular_fit()
} else if (strategy == "remove") {
    if (!file.exists(paste0(output_path, "/MutationalPatterns_regular.txt"))) {
        regular_fit()
    }
    strict_remove()
} else {
    # STUB refit_general also
    strict_refit()
}