import sys
import logging
import json

from parsl.executors import ThreadPoolExecutor
from parsl.config import Config

from apps.parsl_bash_apps import *

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

    sample_path = assignment_config['required']['samples']
    reference_path = assignment_config['required']['reference']
    output_path = assignment_config['required']['output']
    strategy = assignment_config['required']['strategy']

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    # Start runs in parallel
    runs = []
    tools = []
    for tool, is_run in assignment_config['tools'].items():
        if not is_run:
            continue
        tools.append(tool)
        runs.append(TOOLS_APPS[tool](sample_path, reference_path, output_path, strategy))

    LOGGER.info("Waiting for Parsl tasks to complete...")
    parsl.wait_for_current_tasks()

    [r.result() for r in runs]

    # Post-processing after all runs are done
    TOOLS_APPS['postprocess'](sample_path, reference_path, output_path, strategy, tools).result()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        main('assignment_config.json')
    else:
        main(sys.argv[1])
