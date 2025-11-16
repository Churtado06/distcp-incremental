
import datetime
import logging

from airflow import models
import airflow.operators.dummy_operator as dummy
from airflow.operators.bash_operator import BashOperator

from google.cloud import storage
from io import StringIO
bash_command_list = []


# --------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------

def read_file_from_bucket(bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob_file = blob.download_as_string()
    blob_file = blob_file.decode('utf-8')
    blob_file = StringIO(blob_file)

    # Returns StringIO file
    content = blob_file.read()
    lines = content.splitlines()

    for i in lines:
        source, dest = i.split(',')
        compound_command = "gcloud dataproc jobs submit hadoop --cluster-labels=cluster-pool=pool-1 --class=org.apache.hadoop.tools.DistCp --region=us-central1 -- -delete -overwrite " + source + " " + dest
        bash_command_list.append(compound_command)

    return bash_command_list


def distcp(command,idx):
    return BashOperator(
        task_id ='bash_distcp_task_'+str(idx),
        bash_command = command)

# --------------------------------------------------------------------------------
# Set default arguments
# --------------------------------------------------------------------------------

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}


# --------------------------------------------------------------------------------
# Set GCP logging
# --------------------------------------------------------------------------------

logger = logging.getLogger('incremental_data_load_log')

# --------------------------------------------------------------------------------
# Main DAG
# --------------------------------------------------------------------------------

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.


with models.DAG(
        'distcp_incremental_data_load_dag',
        start_date = datetime.datetime(2021, 12, 13),
        default_args = default_args,
        schedule_interval = None) as dag:
    

    start = dummy.DummyOperator(
        task_id = 'start',
        trigger_rule ='all_success'
    )

    end = dummy.DummyOperator(
        task_id ='end',
        trigger_rule ='all_success'
    )

    try:
        bash_command_list = read_file_from_bucket(bucket_name = "audit-file-distcp-bucket1", file_name = "folders_to_copy.txt")
    except Exception as e:
        print("Error reading folders to copy in GCS.")
        print(e)

    for idx, command in enumerate(bash_command_list):
        start >> distcp(command,idx) >> end