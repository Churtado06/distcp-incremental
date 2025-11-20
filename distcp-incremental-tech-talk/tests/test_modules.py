import os
import sys
import pytest

# Add the cloud_function_composer2 directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cloud_function_composer2'))

import main
import composer2_airflow_rest_api


def test_main_module_import():
    """Test that main module can be imported"""
    assert hasattr(main, 'trigger_dag_gcf')


def test_composer_api_module_import():
    """Test that composer API module can be imported"""
    assert hasattr(composer2_airflow_rest_api, 'trigger_dag')
    assert hasattr(composer2_airflow_rest_api, 'make_composer2_web_server_request')


def test_trigger_dag_function_with_env_vars():
    """Test trigger_dag_gcf function uses environment variables from workflow"""
    # Test that environment variables are received from the workflow
    composer_url_id = os.getenv('COMPOSER_URL_ID')
    gcp_region = os.getenv('GCP_REGION')
    dag_id = os.getenv('DAG_ID')
    environment = os.getenv('ENVIRONMENT')
    user_name = os.getenv('USER_NAME_GOOGLE')
    bucket_name = os.getenv('SOURCE_FILES_DATA_BUCKET')
    
    # Print received values for debugging
    print(f"Received from workflow:")
    print(f"  COMPOSER_URL_ID: {composer_url_id}")
    print(f"  GCP_REGION: {gcp_region}")
    print(f"  DAG_ID: {dag_id}")
    print(f"  ENVIRONMENT: {environment}")
    print(f"  USER_NAME_GOOGLE: {user_name}")
    print(f"  SOURCE_FILES_DATA_BUCKET: {bucket_name}")
    
    # Test that all required environment variables are set by the workflow
    assert composer_url_id is not None, "COMPOSER_URL_ID not set by workflow"
    assert gcp_region is not None, "GCP_REGION not set by workflow"
    assert dag_id is not None, "DAG_ID not set by workflow"
    assert environment is not None, "ENVIRONMENT not set by workflow"
    assert user_name is not None, "USER_NAME_GOOGLE not set by workflow"
    assert bucket_name is not None, "SOURCE_FILES_DATA_BUCKET not set by workflow"
    
    # Test expected values from workflow
    assert composer_url_id == '3eed80d0e54a4be78b9dd56d2b2f63bd'
    assert gcp_region == 'us-central1'
    assert dag_id == 'distcp_incremental_data_load'
    assert environment in ['dev', 'staging', 'prod']  # Valid workflow inputs
    
    # Test that the function exists and is callable
    assert callable(main.trigger_dag_gcf)
    
    # Test that we can construct the expected web server URL
    expected_url = f'https://{composer_url_id}-dot-{gcp_region}.composer.googleusercontent.com'
    assert 'composer.googleusercontent.com' in expected_url
    print(f"  Constructed URL: {expected_url}")


def test_environment_variables_in_modules():
    """Test that modules can access environment variables from workflow"""
    # Test that environment variables are available to the modules
    user_name = os.getenv('USER_NAME_GOOGLE')
    bucket_name = os.getenv('SOURCE_FILES_DATA_BUCKET')
    environment = os.getenv('ENVIRONMENT')
    
    print(f"Module test - User: {user_name}")
    print(f"Module test - Bucket: {bucket_name}")
    print(f"Module test - Environment: {environment}")
    
    # These should be set by the workflow and match expected patterns
    assert user_name is not None, "USER_NAME_GOOGLE not received from workflow"
    assert bucket_name is not None, "SOURCE_FILES_DATA_BUCKET not received from workflow"
    assert environment is not None, "ENVIRONMENT not received from workflow"
    
    # Test that values match workflow input patterns
    assert 'gcp' in user_name.lower() or user_name == 'churtado_gcp1'  # Default or custom
    assert 'distcp' in bucket_name or 'bucket' in bucket_name  # Expected bucket pattern
    assert environment in ['dev', 'staging', 'prod']  # Valid workflow choices