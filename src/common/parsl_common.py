import os
import logging

from parsl.executors import ThreadPoolExecutor
from parsl.config import Config
from parsl.data_provider.files import File
from parsl.dataflow.memoization import id_for_memo

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def get_parsl_config_local(job_config, logs_path):
    if not os.path.isdir(logs_path):
        os.makedirs(logs_path, exist_ok=True)
    return Config(
        run_dir=logs_path,
        executors=[
            ThreadPoolExecutor(
                label="ensemblefit-job-executor",
                thread_name_prefix=f"job-{job_config['job_id']}",
                max_threads=4
            )
        ],
        retries=3,
        app_cache=False,
        checkpoint_mode='task_exit'
    )


# checkpoints based on file attributes
# Refer to https://github.com/Parsl/parsl/issues/1603
@id_for_memo.register(File)
def id_for_memo_file(file, output_ref=False):
    LOGGER.debug(f"[id_for_memo_file] Hashing file: {file}, output_ref: {output_ref}")
    if output_ref:
        return file.url
    else:
        assert file.scheme == "file"
        if os.path.exists(file):
            stat_result = os.stat(file.filepath)
            memo_result = [file.url, stat_result.st_size]
            LOGGER.info(f"[id_for_memo_file] Hashed memo_result: {memo_result}, file: {file}, output_ref: {output_ref}")
            return memo_result
        else:
            LOGGER.warning(f"[id_for_memo_file] Missing file: {file}, output_ref: {output_ref}")
            return "false"
