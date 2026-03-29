import pytest
from moto import mock_aws
import boto3
from freezegun import freeze_time
from lambdas.daily_tweet_scheduler.schedule_tweets import lambda_handler
import os
from datetime import datetime


@mock_aws
@freeze_time("2024-03-15")
def test_schedule_tweets_success(mock_env_vars, mocker, mock_sqs):
    """Test successful album scheduling"""
    
    # Mock database response - release_date should be a datetime object
    mock_db = mocker.patch('lambdas.daily_tweet_scheduler.schedule_tweets.DatabaseManager')
    mock_db.return_value.fetch_by_release_date.return_value = [
        (1, "To Pimp a Butterfly", "Kendrick Lamar", "rap", datetime(2015, 3, 15), "Reviewer", datetime(2015, 3, 16), "http://image.jpg")
        # Changed "2015-03-15" to datetime(2015, 3, 15) ↑
    ]
    
    # Set queue URL
    os.environ["TWEET_QUEUE_URL"] = mock_sqs
    
    # Invoke Lambda
    result = lambda_handler({}, {})
    
    # Assertions
    assert result["status"] == "queued"
    assert result["count"] == 1
    
    # Verify SQS message
    sqs = boto3.client("sqs", region_name="us-east-1")
    messages = sqs.receive_message(QueueUrl=mock_sqs)
    assert len(messages.get('Messages', [])) == 1

@mock_aws
def test_schedule_tweets_no_albums(mock_env_vars, mocker, mock_sqs):
    """Test when no albums found for today"""
    
    mock_db = mocker.patch('lambdas.daily_tweet_scheduler.schedule_tweets.DatabaseManager')
    mock_db.return_value.fetch_by_release_date.return_value = []
    
    os.environ["TWEET_QUEUE_URL"] = mock_sqs
    
    result = lambda_handler({}, {})
    
    assert result["count"] == 0