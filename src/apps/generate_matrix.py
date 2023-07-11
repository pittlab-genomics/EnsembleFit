import os
import sys
import shutil
from SigProfilerMatrixGenerator.scripts import SigProfilerMatrixGeneratorFunc as matGen


def main(vcf_dir, genome, project='mutsig'):
    assert genome in ('GRCh37', 'GRCh38', 'mm39', 'mm10', 'mm9')
    matrices = matGen.SigProfilerMatrixGeneratorFunc(project,
                                                    genome,
                                                    vcf_dir,
                                                    exome=False,
                                                    bed_file=None,
                                                    chrom_based=False,
                                                    plot=False,
                                                    tsb_stat=False,
                                                    seqInfo=False)
    # TODO: Remove unnecessary dir and files except for catalogue?


if __name__ == '__main__':
    vcf_dir = sys.argv[1]
    genome = sys.argv[2]
    main(vcf_dir, genome)
