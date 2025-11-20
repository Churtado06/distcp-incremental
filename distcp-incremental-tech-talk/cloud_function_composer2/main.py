# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Trigger a DAG in a Cloud Composer 2 environment in response to an event,
using Cloud Functions.
"""


import os
import composer2_airflow_rest_api


def trigger_dag_gcf(data, context=None):
    """
    Trigger a DAG and pass event data.

    Args:
      data: A dictionary containing the data for the event. Its format depends
      on the event.
      context: The context object for the event.

    For more information about the arguments, see:
    https://cloud.google.com/functions/docs/writing/background#function_parameters
    """

    # Get configuration from environment variables
    url = os.getenv('COMPOSER_URL_ID', '3eed80d0e54a4be78b9dd56d2b2f63bd')
    region = os.getenv('GCP_REGION', 'us-central1')
    web_server_url = (
        f"https://{url}-dot-{region}.composer.googleusercontent.com"
    )
    # Get DAG ID from environment variable
    dag_id = os.getenv('DAG_ID', 'distcp_incremental_data_load')

    # Add environment context to data
    environment = os.getenv('ENVIRONMENT', 'dev')
    user_name = os.getenv('USER_NAME_GOOGLE', 'default_user')
    bucket_name = os.getenv('SOURCE_FILES_DATA_BUCKET', 'default-bucket')

    # Enhance data with environment variables
    enhanced_data = {
        **data,
        'environment': environment,
        'user_name': user_name,
        'source_bucket': bucket_name,
        'region': region
    }

    composer2_airflow_rest_api.trigger_dag(web_server_url, dag_id, enhanced_data)
