import pytest
import responses
from lib.pitchfork_scraper import PitchforkScraper

@responses.activate
def test_get_album_release_date_success(mock_env_vars, mocker):
    """Test MusicBrainz API success"""
    
    # Mock MusicBrainz response
    responses.add(
        responses.GET,
        "https://musicbrainz.org/ws/2/release/",
        json={
            "releases": [
                {
                    "date": "2015-03-15",
                    "status": "Official",
                    "disambiguation": ""
                }
            ]
        },
        status=200
    )
    
    # Mock database and driver
    mocker.patch('lib.pitchfork_scraper.DatabaseManager')
    mocker.patch('lib.pitchfork_scraper.webdriver.Chrome')
    
    scraper = PitchforkScraper()
    result = scraper.get_album_release_date("To Pimp a Butterfly", "Kendrick Lamar")
    
    assert result == "2015-03-15"

@responses.activate
def test_get_album_release_date_filters_anniversary(mock_env_vars, mocker):
    """Test filtering out anniversary editions"""
    
    responses.add(
        responses.GET,
        "https://musicbrainz.org/ws/2/release/",
        json={
            "releases": [
                {
                    "date": "2025-03-15",
                    "status": "Official",
                    "disambiguation": "10th Anniversary Edition"
                },
                {
                    "date": "2015-03-15",
                    "status": "Official",
                    "disambiguation": ""
                }
            ]
        },
        status=200
    )
    
    mocker.patch('lib.pitchfork_scraper.DatabaseManager')
    mocker.patch('lib.pitchfork_scraper.webdriver.Chrome')
    
    scraper = PitchforkScraper()
    result = scraper.get_album_release_date("Album", "Artist")
    
    # Should return original release, not anniversary
    assert result == "2015-03-15"