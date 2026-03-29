import pytest
from unittest.mock import Mock, patch
from lib.twitter_bot import TwitterBot

def test_post_album_anniversary_success(mock_env_vars, mocker):
    """Test successful tweet posting"""
    
    # Mock Tweepy client
    mock_client = mocker.patch('lib.twitter_bot.tweepy.Client')
    mock_response = Mock()
    mock_response.data = {'id': '123456789'}
    mock_client.return_value.create_tweet.return_value = mock_response
    
    # Create bot and post
    bot = TwitterBot()
    result = bot.post_album_anniversary("Kendrick Lamar", "To Pimp a Butterfly", "2015-03-15")
    
    # Verify
    assert "123456789" in result
    mock_client.return_value.create_tweet.assert_called_once()

def test_post_album_anniversary_error(mock_env_vars, mocker):
    """Test error handling in tweet posting"""
    
    mock_client = mocker.patch('lib.twitter_bot.tweepy.Client')
    mock_client.return_value.create_tweet.side_effect = Exception("API Error")
    
    bot = TwitterBot()
    
    # Should raise exception (changed behavior)
    with pytest.raises(Exception, match="API Error"):  # ← UPDATE THIS LINE
        bot.post_album_anniversary("Artist", "Album", "2024-01-01")