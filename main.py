from lib.config import DB_URL
from lib.db_manager import DatabaseManager
from lib.pitchfork_scraper import PitchforkScraper
import datetime
from lib.twitter_bot import TwitterBot

def update_db_from_pitchfork():
    pitchfork_scraper = PitchforkScraper()
    pitchfork_scraper.scrape_all_genres()
    

def tweet_anniversaries():
    db = DatabaseManager()
    twitter = TwitterBot()
    today = datetime.datetime.now().isoformat()[:10]
    print("Fetching records for date:", today)
    records = db.fetch_by_release_date(today)
    print(f"Found {len(records)} records for today.")
    for artist, album, date in records:
        twitter.post_album_anniversary(artist, album, date)

if __name__ == "__main__":
    #update_db_from_pitchfork()  # Uncomment when needed
    tweet_anniversaries()

