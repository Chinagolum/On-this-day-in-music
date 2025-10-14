from config import DB_PATH
from db_manager import DatabaseManager
from scraper import PitchforkScraper
from twitter_bot import TwitterBot
import datetime

def update_db_from_pitchfork():
    db = DatabaseManager(DB_PATH)
    scraper = PitchforkScraper()
    artist_links = scraper.get_artist_links("https://pitchfork.com/artists/by/genre/rap/")

    for artist, link in artist_links.items():
        albums = scraper.get_artist_albums(link)
        for album, date in albums:
            db.insert_entry(artist, album, date)

    db.commit_and_close()

def tweet_anniversaries():
    db = DatabaseManager(DB_PATH)
    twitter = TwitterBot()
    today = datetime.datetime.now().isoformat()[:10]

    records = db.fetch_by_date(today)
    for aID, artist, album, date in records:
        twitter.post_album_anniversary(artist, album, date)

    db.commit_and_close()

if __name__ == "__main__":
    # update_db_from_pitchfork()  # Uncomment when needed
    tweet_anniversaries()
