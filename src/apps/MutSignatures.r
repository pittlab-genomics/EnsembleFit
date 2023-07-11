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
library(mutSignatures)

cat(paste0("[", Sys.time(), "] Start"), "\n")
##############################
# REGULAR FITTING
##############################
regular_fit <- function() {
    matrix <- read.delim(sample_path, sep="\t", row.names=1)
    #matrix <- read.delim(sample_path, sep="\t")
    #matrix <- setNames(data.frame(t(matrix[,-1])), matrix[,1])
    #matrix <- as.data.frame(t(matrix))
    mutation_counts <- as.mutation.counts(matrix)

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var=colnames(ref)[1])
    mutation_signatures <- as.mutation.signatures(ref)

    res <- resolveMutSignatures(mutCountData=mutation_counts, 
                                signFreqData=mutation_signatures)
    regular <- as.data.frame(t(res$results$count.result@exposures))
    colnames(regular) <- res$results$count.result@signatureId$ID
    rownames(regular) <- res$results$count.result@sampleId$ID
    regular <- tibble::rownames_to_column(regular, "Samples")

    write.table(regular, paste0(output_path, "/MutSignatures_regular.txt"), sep="\t", quote=FALSE, row.name=FALSE)
    cat(paste0("[", Sys.time(), "] Regular DONE"), "\n")
}
##############################
# REMOVE
##############################
strict_remove <- function() {
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))
    total_mutations <- colSums(matrix)

    regular <- read.delim(paste0(output_path, "/MutSignatures_regular.txt"), sep="\t")
    remove <- regular
    unassigned <- rep(NA, nrow(remove))
    for (i in 1:nrow(regular)) {
        new_row <- apply(regular[i, 2:ncol(regular)], 2, function(x) { ifelse(x < total_mutations[i] * 0.05, 0, x) })
        remove[i, 2:ncol(regular)] <- new_row
        unassigned[i] <- total_mutations[i] - sum(new_row)
    }
    remove$unassigned <- unassigned

    write.table(remove, paste0(output_path, "/MutSignatures_remove.txt"), sep="\t", quote=FALSE, row.name=FALSE)
    cat(paste0("[", Sys.time(), "] Remove DONE"), "\n")
}
##############################
# STRICT REFIT
##############################
strict_refit <- function(include_sigs=c()) {
    has_include_sigs <- length(include_sigs) > 0
    matrix <- as.matrix(read.delim(sample_path, sep="\t", row.names=1))
    total_mutations <- colSums(matrix)

    ref <- read.delim(reference_path, sep="\t")
    ref <- ref %>% column_to_rownames(., var=colnames(ref)[1])

    regular <- read.delim(paste0(output_path, "/MutSignatures_regular.txt"), sep="\t")

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
        matrix_single <- as.data.frame(matrix[i,])
        # if only 1 reference signature in the subset, no assignment
        if (length(ref_subset) == 1) {
            sample_name <- rownames(matrix)[i]
            sample_count <- sum(matrix_single)/1.0
            exposures <- data.frame(Samples=sample_name, 
                                    SIG=sample_count)
            colnames(exposures) <- c("Samples", colnames(ref_subset))
            refit <- dplyr::bind_rows(refit, exposures)
            next
        }
        # standard assignment
        colnames(matrix_single) <- c(row.names(matrix)[i])
        mutation_counts <- as.mutation.counts(matrix_single)
        mutation_signatures <- as.mutation.signatures(ref_subset)
        single_res <- resolveMutSignatures(mutCountData=mutation_counts,
                                            signFreqData=mutation_signatures)
        exposures <- as.data.frame(t(single_res$results$count.result@exposures))
        colnames(exposures) <- single_res$results$count.result@signatureId$ID
        rownames(exposures) <- single_res$results$count.result@sampleId$ID
        exposures <- tibble::rownames_to_column(exposures, "Samples")
        refit <- dplyr::bind_rows(refit, exposures)   
    }
    refit <- refit %>% replace(is.na(.), 0)

    # Rearrange signature columns
    sigs_col <- colnames(ref)
    sigs_col <- sigs_col[sigs_col %in% colnames(refit)]
    refit <- refit[c("Samples", sigs_col)]

    write.table(refit, paste0(output_path, "/MutSignatures_refit.txt"), sep="\t", quote=FALSE, row.name=FALSE)
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
    if (!file.exists(paste0(output_path, "/MutSignatures_regular.txt"))) {
        regular_fit()
    }
    strict_remove()
} else if (strategy == "refit_general") {
    if (!file.exists(paste0(output_path, "/MutSignatures_regular.txt"))) {
        regular_fit()
    }
    strict_refit()
} else {
    # refit with specific signatures - For now hardcode SBS1 and SBS5
    if (!file.exists(paste0(output_path, "/MutSignatures_regular.txt"))) {
        regular_fit()
    }
    if (grepl("COSMICv3", reference_path)) {
        include_sigs <- c("SBS1", "SBS5")
    } else {
        include_sigs <- c("Signature_1", "Signature_5")
    }
    strict_refit(include_sigs)
}