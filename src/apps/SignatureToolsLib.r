args <- commandArgs(trailingOnly=TRUE)
if (length(args) < 4) {
    stop("Need 4 arguments: sample_path reference_path output_path strategy", call.=FALSE)
}
sample_path <- args[1]
reference_path <- args[2]
output_path <- args[3]
strategy <- args[4]
toolname <- "SignatureToolsLib"

if (!dir.exists(output_path)) {
    dir.create(output_path)
}

library(tidyverse)
library(tibble)
library(signature.tools.lib)
##############################
# REGULAR
##############################
regular_fit <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var=colnames(ref)[1])

    regular <- Fit(matrix, ref, threshold_percent=0)
    regular <- regular$exposures
    regular <- tibble::rownames_to_column(as.data.frame(regular), "Samples")

    write.table(regular, paste0(output_path, "/", toolname, "_regular.txt"), sep="\t", quote=FALSE, row.name=FALSE)
}
##############################
# REMOVE
##############################
strict_remove <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var=colnames(ref)[1])

    remove <- Fit(matrix, ref, threshold_percent=5)
    remove <- remove$exposures
    remove <- tibble::rownames_to_column(as.data.frame(remove), "Samples")

    write.table(remove, paste0(output_path, "/", toolname, "_remove.txt"), sep="\t", quote=FALSE, row.name=FALSE)
}
##############################
# REFIT
##############################
strict_refit <- function(include_sigs=c()) {
    has_include_sigs <- length(include_sigs) > 0
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))
    total_mutations <- colSums(matrix)

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var=colnames(ref)[1])

    regular <- read.delim(paste0(output_path, "/", toolname, "_regular.txt"), sep="\t")

    # Convert assignment to percentage
    for (i in c(1:nrow(regular))) {
        regular[i, 2:ncol(regular)] <- regular[i, 2:ncol(regular)] / total_mutations[i]
    }

    # Identify reference subset for each sample
    # Matrix needs to be (N x 96)
    matrix <- t(matrix)
    subsets <- list()
    for (i in c(1:nrow(matrix))) {
        sigs <- c()
        for (j in c(2:ncol(regular))) {
            sig <- colnames(regular)[j]
            if (regular[i, sig] >= 0.05) {
                sigs <- c(sigs, sig)
            }
        }
        # Include forced signatures if any
        if (has_include_sigs) {
            for (sig in include_sigs) {
                if (!sig %in% sigs) { sigs <- c(sigs, sig) }
            }
        }
        subsets[[i]] <- sigs
    }

    # Fit subset signatures for each sample
    refit <- data.frame(Samples=c())
    for (i in c(1:nrow(matrix))) {
        ref_subset <- ref[subsets[[i]]]
        matrix_single <- as.matrix(matrix[i,])
        single_res <- Fit(matrix_single, ref_subset, threshold_percent=0)$exposures
        row.names(single_res) <- c(row.names(matrix)[i])
        single_res <- tibble::rownames_to_column(as.data.frame(single_res), "Samples")
        refit <- dplyr::bind_rows(refit, single_res)
    }
    refit <- refit %>% replace(is.na(.), 0)

    # Rearrange signature columns
    sigs_col <- colnames(ref)
    sigs_col <- sigs_col[sigs_col %in% colnames(refit)]
    refit <- refit[c("Samples", sigs_col)]

    write.table(refit, paste0(output_path, "/", toolname, "_refit.txt"), sep="\t", quote=FALSE, row.name=FALSE)
}
##############################
# MAIN
##############################
cat(paste0("[", Sys.time(), "] Start"), "\n")
cat(paste0("    - Sample Path: ", sample_path), "\n")
cat(paste0("    - Reference Path: ", reference_path), "\n")
cat(paste0("    - Output Path: ", output_path), "\n")
cat(paste0("    - Strategy: ", strategy), "\n")

if (!file.exists(paste0(output_path, "/", toolname, "_regular.txt"))) {
    regular_fit()
    cat(paste0("[", Sys.time(), "] Regular DONE"), "\n")
}
if (strategy == "remove") {
    strict_remove()
    cat(paste0("[", Sys.time(), "] Remove DONE"), "\n")
} else if (strategy == "refit_general") {
    strict_refit()
    cat(paste0("[", Sys.time(), "] Refit DONE"), "\n")
} else {
    # refit with specific signatures - For now force SBS1 and SBS5
    if (grepl("COSMICv3", reference_path)) {
        include_sigs <- c("SBS1", "SBS5")
    } else {
        include_sigs <- c("Signature_1", "Signature_5")
    }
    strict_refit(include_sigs)
    cat(paste0("[", Sys.time(), "] Refit DONE"), "\n")
}