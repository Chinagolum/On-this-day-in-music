import pytest
import json
from moto import mock_aws
import boto3
from unittest.mock import Mock
from lambdas.tweet_poster.create_tweet import lambda_handler, handle_tweet_request

@mock_aws
def test_lambda_handler_success(mock_env_vars, mocker):
    """Test successful tweet processing from SQS"""
    
    # Mock TwitterBot
    mock_twitter = mocker.patch('lambdas.tweet_poster.create_tweet.twitter')
    mock_twitter.post_album_anniversary.return_value = "Tweet posted: 123456"
    
    # Create SQS event
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'artist': 'Kendrick Lamar',
                    'album': 'To Pimp a Butterfly',
                    'release_date': '2015-03-15'
                })
            }
        ]
    }
    
    # Invoke Lambda
    result = lambda_handler(event, {})
    
    # Assertions
    assert result['statusCode'] == 200
    assert len(result['results']) == 1
    assert result['results'][0]['status'] == 'tweeted'
    
    # Verify TwitterBot was called
    mock_twitter.post_album_anniversary.assert_called_once_with(
        'Kendrick Lamar',
        'To Pimp a Butterfly',
        '2015-03-15'
    )

@mock_aws
def test_lambda_handler_missing_fields(mock_env_vars, mocker):
    """Test handling of invalid message data"""
    
    mock_twitter = mocker.patch('lambdas.tweet_poster.create_tweet.twitter')
    
    # Missing 'album' field
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'artist': 'Kendrick Lamar',
                    'release_date': '2015-03-15'
                })
            }
        ]
    }
    
    result = lambda_handler(event, {})
    
    # Should return failed status
    assert result['results'][0]['status'] == 'failed'
    
    # TwitterBot should NOT be called
    mock_twitter.post_album_anniversary.assert_not_called()

@mock_aws
def test_lambda_handler_twitter_error(mock_env_vars, mocker):
    """Test error handling when Twitter API fails"""
    
    mock_twitter = mocker.patch('lambdas.tweet_poster.create_tweet.twitter')
    mock_twitter.post_album_anniversary.side_effect = Exception("Twitter API Error")
    
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'artist': 'Kendrick Lamar',
                    'album': 'To Pimp a Butterfly',
                    'release_date': '2015-03-15'
                })
            }
        ]
    }
    
    # Should raise exception (which tells SQS to retry)
    with pytest.raises(Exception, match="Twitter API Error"):
        lambda_handler(event, {})

def test_handle_tweet_request_success(mock_env_vars, mocker):
    """Test handle_tweet_request with valid data"""
    
    mock_twitter = mocker.patch('lambdas.tweet_poster.create_tweet.twitter')
    mock_twitter.post_album_anniversary.return_value = "Success"
    
    message_body = json.dumps({
        'artist': 'Artist',
        'album': 'Album',
        'release_date': '2020-01-01'
    })
    
    result = handle_tweet_request(message_body)
    
    assert result['status'] == 'tweeted'
    assert 'Success' in result['message']

def test_handle_tweet_request_invalid_json(mock_env_vars):
    """Test handling of malformed JSON"""
    
    with pytest.raises(json.JSONDecodeError):
        handle_tweet_request("not valid json")

@mock_aws
def test_lambda_handler_multiple_messages(mock_env_vars, mocker):
    """Test processing multiple SQS messages in batch"""
    
    mock_twitter = mocker.patch('lambdas.tweet_poster.create_tweet.twitter')
    mock_twitter.post_album_anniversary.return_value = "Tweet posted"
    
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'artist': 'Artist 1',
                    'album': 'Album 1',
                    'release_date': '2020-01-01'
                })
            },
            {
                'body': json.dumps({
                    'artist': 'Artist 2',
                    'album': 'Album 2',
                    'release_date': '2021-02-02'
                })
            }
        ]
    }
    
    result = lambda_handler(event, {})
    
    assert result['statusCode'] == 200
    assert len(result['results']) == 2
    
    # Verify TwitterBot was called twice
    assert mock_twitter.post_album_anniversary.call_count == 2