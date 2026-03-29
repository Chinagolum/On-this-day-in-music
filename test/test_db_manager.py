import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from lib.db_manager import DatabaseManager

@pytest.fixture
def mock_db_connection(mocker):
    """Mock psycopg2 database connection"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mocker.patch('lib.db_manager.psycopg2.connect', return_value=mock_conn)
    
    return mock_conn, mock_cursor

def test_init_creates_table(mock_db_connection, mock_env_vars):
    """Test DatabaseManager initialization creates table"""
    mock_conn, mock_cursor = mock_db_connection
    
    db = DatabaseManager()
    
    # Verify connection was made
    assert db.conn == mock_conn
    assert db.c == mock_cursor
    
    # Verify create_table was called
    mock_cursor.execute.assert_called()
    assert 'CREATE TABLE IF NOT EXISTS albums' in mock_cursor.execute.call_args[0][0]

def test_insert_entry_success(mock_db_connection, mock_env_vars):
    """Test successful album insertion"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 1  # Simulate successful insert
    
    db = DatabaseManager()
    
    db.insert_entry(
        title="To Pimp a Butterfly",
        artist="Kendrick Lamar",
        genre="rap",
        release_date="2015-03-15",
        reviewer="Reviewer",
        review_date="2015-03-16",
        image_url="http://image.jpg"
    )
    
    # Verify INSERT was called
    insert_call = [call for call in mock_cursor.execute.call_args_list 
                   if 'INSERT INTO albums' in str(call)]
    assert len(insert_call) > 0
    
    # Verify commit was called
    mock_conn.commit.assert_called()

def test_insert_entry_duplicate(mock_db_connection, mock_env_vars):
    """Test duplicate insertion is skipped"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.rowcount = 0  # Simulate ON CONFLICT DO NOTHING
    
    db = DatabaseManager()
    
    db.insert_entry(
        title="Album",
        artist="Artist",
        genre="rock"
    )
    
    # Should still commit (no error)
    mock_conn.commit.assert_called()

def test_insert_entry_missing_required_fields(mock_db_connection, mock_env_vars):
    """Test insertion fails without required fields"""
    db = DatabaseManager()
    
    with pytest.raises(ValueError, match="title and artist are required"):
        db.insert_entry(title="Album", artist=None)
    
    with pytest.raises(ValueError, match="title and artist are required"):
        db.insert_entry(title=None, artist="Artist")

def test_fetch_by_release_date_success(mock_db_connection, mock_env_vars):
    """Test fetching albums by release date"""
    mock_conn, mock_cursor = mock_db_connection
    
    # Mock database return value
    mock_cursor.fetchall.return_value = [
        (1, "Album 1", "Artist 1", "rap", datetime(2015, 3, 15), "Reviewer", datetime(2015, 3, 16), "http://img1.jpg"),
        (2, "Album 2", "Artist 2", "rock", datetime(2010, 3, 15), "Reviewer", datetime(2010, 3, 16), "http://img2.jpg")
    ]
    
    db = DatabaseManager()
    results = db.fetch_by_release_date("2024-03-15")
    
    # Verify query was called with correct month-day
    execute_calls = mock_cursor.execute.call_args_list
    fetch_call = [call for call in execute_calls if 'TO_CHAR' in str(call)]
    assert len(fetch_call) > 0
    assert '03-15' in str(fetch_call[0])
    
    # Verify results
    assert len(results) == 2

def test_fetch_by_release_date_invalid_format(mock_db_connection, mock_env_vars):
    """Test error handling for invalid date format"""
    db = DatabaseManager()
    
    with pytest.raises(ValueError, match="must be in 'YYYY-MM-DD' format"):
        db.fetch_by_release_date("2024/03/15")
    
    with pytest.raises(ValueError, match="must be in 'YYYY-MM-DD' format"):
        db.fetch_by_release_date("03-15-2024")
    
    with pytest.raises(ValueError, match="must be in 'YYYY-MM-DD' format"):
        db.fetch_by_release_date(None)

def test_fetch_by_review_date_success(mock_db_connection, mock_env_vars):
    """Test fetching albums by review date"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = []
    
    db = DatabaseManager()
    results = db.fetch_by_review_date("2024-03-15")
    
    # Verify query was called
    execute_calls = mock_cursor.execute.call_args_list
    review_call = [call for call in execute_calls if 'review_date' in str(call)]
    assert len(review_call) > 0

def test_fetch_all_success(mock_db_connection, mock_env_vars):
    """Test fetching all albums"""
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        (1, "Album 1", "Artist 1", "rap", None, None, None, None),
        (2, "Album 2", "Artist 2", "rock", None, None, None, None)
    ]
    
    db = DatabaseManager()
    results = db.fetch_all()
    
    # Verify ORDER BY release_date
    execute_calls = mock_cursor.execute.call_args_list
    fetch_all_call = [call for call in execute_calls if 'ORDER BY release_date' in str(call)]
    assert len(fetch_all_call) > 0
    
    assert len(results) == 2

def test_close_connection(mock_db_connection, mock_env_vars):
    """Test closing database connection"""
    mock_conn, mock_cursor = mock_db_connection
    
    db = DatabaseManager()
    db.close()
    
    # Verify connection was closed
    mock_conn.close.assert_called_once()

def test_close_connection_already_closed(mock_db_connection, mock_env_vars):
    """Test closing already closed connection doesn't error"""
    mock_conn, mock_cursor = mock_db_connection
    
    db = DatabaseManager()
    db.conn = None
    
    # Should not raise error
    db.close()