import sys
import logging
import json
import shutil

from parsl.executors import ThreadPoolExecutor
from parsl.config import Config

from apps.parsl_bash_apps import *
import apps.workflow_utils as utils

LOGS_PATH = 'logs'
LOGGER = logging.getLogger('ensemblefit')


def get_parsl_config_local():
    return Config(
        run_dir=LOGS_PATH,
        executors=[ThreadPoolExecutor()],
        retries=3,
        app_cache=True,
        checkpoint_mode='task_exit'
    )


def main(config_path):
    if not os.path.isdir(LOGS_PATH):
        os.mkdir(LOGS_PATH)
    parsl.set_stream_logger("parsl", logging.INFO)
    parsl.load(get_parsl_config_local())

    # Read config file
    with open(config_path) as f:
        assignment_config = json.load(f)

    reference_path = assignment_config['signature_reference']
    output_path = assignment_config['output']
    strategy = assignment_config['strategy']

    # Create output directory
    os.makedirs(output_path, exist_ok=True)
    
    # Create working directory and results directory
    WORKINGDIR = os.path.join(output_path, 'temp')
    RESULTDIR = os.path.join(output_path, 'results')
    os.makedirs(WORKINGDIR, exist_ok=True)
    os.makedirs(RESULTDIR, exist_ok=True)

    # Copy of input samples matrix
    sample_path = os.path.join(WORKINGDIR, 'samples.txt')

    # Matrix generation if needed
    if assignment_config['file_type'] == 'vcf':
        vcf_path = assignment_config['samples']
        genome_reference = assignment_config['genome_reference']
        TOOLS_APPS['generate_matrix'](vcf_path, genome_reference).result()
        # Move all output files to working directory
        shutil.move(os.path.join(vcf_path, 'output/SBS/mutsig.SBS96.all'), sample_path)
        os.makedirs(os.path.join(WORKINGDIR, 'SigProfilerMatrixGenerator'), exist_ok=True)
        shutil.move(os.path.join(vcf_path, 'input'), os.path.join(WORKINGDIR, 'SigProfilerMatrixGenerator', 'input'))
        shutil.move(os.path.join(vcf_path, 'logs'), os.path.join(WORKINGDIR, 'SigProfilerMatrixGenerator', 'logs'))
    else:
        # Format matrix's SBS96 order to match the signature reference and save to working directory
        utils.format_matrix(assignment_config['samples'], reference_path, sample_path)

    # Check if matrix is valid
    if not utils.is_valid_matrix(sample_path):
        throw_invalid_matrix_error(sample_path)

    # Start runs in parallel
    runs = []
    tools = []
    for tool, is_run in assignment_config['tools'].items():
        if not is_run:
            continue
        tools.append(tool)
        runs.append(TOOLS_APPS[tool](sample_path, reference_path, WORKINGDIR, strategy))

    LOGGER.info("Waiting for Parsl tasks to complete...")
    parsl.wait_for_current_tasks()

    [r.result() for r in runs]

    # EnsembleFit
    TOOLS_APPS['EnsembleFit'](sample_path, reference_path, WORKINGDIR, strategy, tools).result()

    # Post-processing after all runs are done
    all_tools = tools + ['Ensemble-Majority', 'Ensemble-Unanimous', 'Ensemble-Mean']
    TOOLS_APPS['postprocess'](sample_path, reference_path, WORKINGDIR, RESULTDIR, strategy, all_tools).result()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        main('assignment_config.json')
    else:
        main(sys.argv[1])
