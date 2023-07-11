import os
import json
import logging
import shutil
import uuid
from datetime import datetime

import boto3

MUTSIG_WORKFLOW_NAME = 'mutsig'
MATRIXGEN_WORKFLOW_NAME = 'matrixgen'
ENSEMBLEFIT_CONDA_ENV = "mutsig_assignment"
CONDA_SOURCE_PATH = "/miniconda/etc/profile.d/conda.sh"

JOB_CONFIG_FILENAME = "manifest.json"
DEFAULT_BASE_WORKDIR_PATH = "/tmp/ensemblefit"

MUTSIG_OUTPUT_FILES = [
    "assignment_metrics.txt",
    "assignment_summary.json",
    "assignment_summary.txt",
    "job_metadata.txt",
    "sbs96_profiles.json",
]
MATRIXGEN_OUTPUT_FILES = [
    "mutsig.SBS96.all",
]

SQS_CLIENT = boto3.client('sqs', region_name="ap-southeast-1")
S3_CLIENT = boto3.resource('s3', region_name='ap-southeast-1')
DYNAMODB_CLIENT = boto3.resource('dynamodb', region_name="ap-southeast-1")

JOB_SUBMISSION_DDB_TABLE_NAME = os.environ['JOB_SUBMISSION_DYNAMODB_TABLE_NAME']
JOB_STATUS_DDB_TABLE_NAME = os.environ['JOB_STATUS_DYNAMODB_TABLE_NAME']
OUTPUT_S3_BUCKET = os.environ['ENSEMBLEFIT_OUTPUTS_S3_BUCKET']

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def update_job_status(ddb_client, ddb_table_name, job_config, message_id, status, workflow, message=None):
    """Update job status in DynamoDB"""
    job_status_table = ddb_client.Table(ddb_table_name)
    job_id = job_config["job_id"]
    LOGGER.info("Updating status in table: %s for job_id: %s, message_id: %s", job_status_table, job_id, message_id)
    time_now = datetime.now()
    response = job_status_table.put_item(
        Item={
            "user_id": job_config["user_id"],
            "job_id": f"{job_id}_{str(uuid.uuid4())}",
            "message_id": message_id,
            "timestamp": int(time_now.timestamp() * 1000),
            "timestamp_iso": time_now.isoformat(),
            "job_status": status,
            "workflow": workflow,
            "message": message or "",
        }
    )
    LOGGER.info("Put item to DynamoDB table: %s", response)


def find_s3_bucket_key(file_item):
    """Find S3 bucket and key for a file item"""
    s3_prefix = "s3://"
    if file_item.startswith(s3_prefix):
        s3_path = file_item[len(s3_prefix):]
        s3_components = s3_path.split("/")
        s3_bucket = s3_components[0]
        s3_key = "/".join(s3_components[1:])
    else:
        s3_bucket = os.environ['ENSEMBLEFIT_UPLOADS_S3_BUCKET']
        s3_key = file_item

    return s3_bucket, s3_key


def download_input_files(s3_client, job_config, input_path, workflow_name):
    if job_config['file_type'] == 'vcf' and workflow_name == MUTSIG_WORKFLOW_NAME:
        upload_files = job_config['upload_matrixgen_files']
    else:
        upload_files = job_config['upload_files']

    for file_item in upload_files:
        s3_bucket, s3_key = find_s3_bucket_key(file_item)
        _, filename = os.path.split(file_item)
        LOGGER.info("Downloading filename: %s, s3_key: %s from s3_bucket: %s", filename, s3_key, s3_bucket)
        s3_client.Bucket(s3_bucket).download_file(s3_key, os.path.join(input_path, filename))
        LOGGER.info("Downloaded filename: %s, input_path: %s", filename, input_path)


def upload_output_files(s3_client, s3_bucket, job_config, output_path, output_files):
    uploaded_files_s3_urls = []
    for filename in output_files:
        if not os.path.isfile(os.path.join(output_path, filename)):
            raise RuntimeError("Could not upload outputs | file not found: %s", filename)
        s3_key = os.path.join(job_config['user_id'], job_config['job_id'], filename)
        LOGGER.info("Uploading filename: %s, s3_key: %s to s3_bucket: %s", filename, s3_key, s3_bucket)
        s3_client.Bucket(s3_bucket).upload_file(os.path.join(output_path, filename), s3_key)
        uploaded_files_s3_urls.append(f"s3://{s3_bucket}/{s3_key}")
    return uploaded_files_s3_urls


def upload_output_archive(s3_client, s3_bucket, job_config, job_workdir_path, output_path, workflow_name):
    user_id = job_config['user_id']
    job_id = job_config['job_id']
    base_filename = f"{workflow_name}_output.zip"
    output_archive_path = os.path.join(job_workdir_path, base_filename)
    shutil.make_archive(os.path.splitext(output_archive_path)[0], "zip", root_dir=job_workdir_path,
                        base_dir=output_path)

    s3_key = os.path.join(user_id, job_id, base_filename)
    LOGGER.info("Uploading output archive: %s, s3_key: %s to s3_bucket: %s", output_archive_path, s3_key, s3_bucket)
    s3_client.Bucket(s3_bucket).upload_file(output_archive_path, s3_key)


def upload_logs_archive(s3_client, s3_bucket, job_config, job_workdir_path, logs_path, workflow_name):
    user_id = job_config['user_id']
    job_id = job_config['job_id']
    base_filename = f"{workflow_name}_logs.zip"
    logs_archive_path = os.path.join(job_workdir_path, base_filename)
    shutil.make_archive(os.path.splitext(logs_archive_path)[0], "zip", root_dir=job_workdir_path, base_dir=logs_path)

    s3_key = os.path.join(user_id, job_id, base_filename)
    LOGGER.info("Uploading logs archive: %s, s3_key: %s to s3_bucket: %s", logs_archive_path, s3_key, s3_bucket)
    s3_client.Bucket(s3_bucket).upload_file(logs_archive_path, s3_key)


def push_to_queue(sqs_client, sqs_queue, job_config):
    LOGGER.info("Pushing to SQS queue: %s", sqs_queue)
    response = sqs_client.send_message(
        QueueUrl=sqs_queue['QueueUrl'],
        DelaySeconds=0,
        MessageBody=json.dumps(job_config),
    )
    LOGGER.info("Sent SQS message: %s", response)


def get_archive_files(workflow_name):
    return [
        f"{workflow_name}_output.zip",
        f"{workflow_name}_logs.zip",
    ]


def get_output_files(job_config):
    result = []
    if job_config['file_type'] == 'vcf':
        result.extend(get_archive_files(MUTSIG_WORKFLOW_NAME))
        result.extend(get_archive_files(MATRIXGEN_WORKFLOW_NAME))
        result.extend(MUTSIG_OUTPUT_FILES + MATRIXGEN_OUTPUT_FILES)
    else:
        result.extend(get_archive_files(MUTSIG_WORKFLOW_NAME))
        result.extend(MUTSIG_OUTPUT_FILES)

    return result
