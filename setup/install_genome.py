import sys

from SigProfilerMatrixGenerator import install as genInstall


def main(ref_genome):
    genInstall.install(ref_genome, rsync=False, bash=True)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        ref_genome = sys.argv[1]
    else:
        ref_genome = 'GRCh37'
    main(ref_genome)
