import pytest
import os
from moto import mock_aws
import boto3

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv("DB_URL", "postgresql://test:test@localhost:5432/test")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")
    monkeypatch.setenv("AWS_BUCKET", "test-bucket")
    monkeypatch.setenv("TWITTER_API_KEY", "test_key")
    monkeypatch.setenv("TWITTER_API_SECRET", "test_secret")
    monkeypatch.setenv("TWITTER_ACCESS_TOKEN", "test_token")
    monkeypatch.setenv("TWITTER_ACCESS_SECRET", "test_access_secret")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")

@pytest.fixture
def mock_sqs():
    """Mock SQS queue"""
    with mock_aws():
        sqs = boto3.client("sqs", region_name="us-east-1")
        queue = sqs.create_queue(QueueName="test-queue")
        yield queue['QueueUrl']

@pytest.fixture
def mock_database(mocker):
    """Mock DatabaseManager for quick tests"""
    mock_db = mocker.MagicMock()
    mocker.patch('lib.db_manager.DatabaseManager', return_value=mock_db)
    return mock_db