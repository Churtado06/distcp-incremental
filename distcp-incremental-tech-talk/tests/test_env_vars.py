import os
import pytest


def test_environment_variables():
    """Test that environment variables are properly set"""
    assert os.getenv('PYTEST_ENV') is not None
    assert os.getenv('TEST_USER') is not None
    assert os.getenv('TEST_BUCKET') is not None
    
    print(f"Testing in environment: {os.getenv('PYTEST_ENV')}")
    print(f"Test user: {os.getenv('TEST_USER')}")
    print(f"Test bucket: {os.getenv('TEST_BUCKET')}")


def test_composer_config():
    """Test Composer configuration"""
    composer_url = os.getenv('COMPOSER_URL_ID')
    dag_id = os.getenv('DAG_ID')
    
    assert composer_url is not None
    assert dag_id is not None
    assert len(composer_url) > 0
    assert dag_id == 'distcp_incremental_data_load'


def test_gcp_region():
    """Test GCP region configuration"""
    region = os.getenv('GCP_REGION')
    assert region is not None
    assert region in ['us-central1', 'us-east1', 'europe-west1']


def test_web_server_url_construction():
    """Test that web server URL can be constructed from env vars"""
    url_id = os.getenv('COMPOSER_URL_ID')
    region = os.getenv('GCP_REGION')
    
    web_server_url = f'https://{url_id}-dot-{region}.composer.googleusercontent.com'
    
    assert 'https://' in web_server_url
    assert 'composer.googleusercontent.com' in web_server_url
    assert url_id in web_server_url
    assert region in web_server_url