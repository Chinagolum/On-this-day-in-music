from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import time
from bs4 import BeautifulSoup
import boto3
from urllib.parse import urlparse, unquote
from datetime import datetime
import os
import logging
from lib.config import *
from lib.db_manager import DatabaseManager
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# ---------- Configure AWS ----------


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

class PitchforkScraper:
    def __init__(self):
        # Disable browser for audit
        self.driver = None
        
        # options = Options()
        # options.binary_location = "/usr/bin/chromium"
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # service = Service("/usr/bin/chromedriver")
        # self.driver = webdriver.Chrome(service=service, options=options)
        
        self.genres = ["rap", "rock", "pop", "jazz", "electronic", "metal", "folk", "experimental"]
        logger.info("Connecting to database...")
        self.database = DatabaseManager()
        self.openai_client = None

    def scroll_down(self, times):
        body = self.driver.find_element("tag name", "body")
        for _ in range(times):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
    
    def upload_image_to_s3(self, image_url, genre, title):
        try:
            logger.info(f"Uploading image for {title} from {image_url}...")
            response = requests.get(image_url)
            logger.info(f"Image download response code: {response.status_code}")
            response.raise_for_status()

            # Create safe filename using genre + title
            ext = os.path.splitext(urlparse(image_url).path)[1] or ".jpg"
            filename = f"{title.replace('/', '_')}{ext}"
            s3_key = f"{genre}/{filename}"

            logger.info(f"Uploading to S3 bucket {AWS_BUCKET} with key {s3_key}...")
            s3.put_object(
                Bucket=AWS_BUCKET,
                Key=s3_key,
                Body=response.content,
                ContentType="image/jpeg",
            )
            logger.info(f"Successfully uploaded {title} to S3.")

            from urllib.parse import quote
            return f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quote(s3_key)}"
        except Exception as e:
            logger.info(f"❌ Failed to upload {title}: {e}")
            return None

    def scrape_all_genres(self):
        for genre in self.genres:
            logger.info(f"\nScraping the genre: {genre}")
            page = 1
            while True:
                logger.info(f"Scraping page {page} of {genre} reviews...")
                url = f"https://pitchfork.com/genre/{genre}/review/?page={page}"
                logger.info(f"\nOpening: {url}")
                self.driver.get(url)
                time.sleep(5)

                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                albums = soup.find_all('div', attrs={'data-item': True, 'role': 'button'})

                if not albums:
                    logger.info("No albums found — likely a blank page. Stopping.")
                    break
                else:
                    logger.info(f"Found {len(albums)} albums on page {page} of {genre}.")

                for album in albums:
                    title_tag = album.find('h3', class_=lambda x: x and 'SummaryItemHedBase' in x)
                    artist_tag = album.find('div', class_=lambda x: x and 'SummaryItemSubHed' in x)
                    reviewer_tag = album.find('span', {'data-testid': 'BylineName'})
                    review_date_tag = album.find('time')
                    image_url_tag = album.find('img')



                    if not title_tag or not artist_tag or not image_url_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    artist = artist_tag.get_text(strip=True)
                    release_date = self.get_album_release_date(title, artist) 
                    reviewer = reviewer_tag.get_text(strip=True)
                    review_date = self.parse_review_date(
                        review_date_tag.get_text(strip=True)
                    )
                    image_url_pf = image_url_tag.get('src') or image_url_tag.get('data-src')

                    if not image_url_pf:
                        logger.warning(f"❌ No image URL for {title} by {artist}")
                        continue   
                    else:
                        logger.info(f"Found image URL for {title} by {artist}: {image_url_pf}")

                    # Upload image to S3
                    logger.info(f"Uploading image for album: {title} by {artist} to S3...")
                    image_url_s3 = self.upload_image_to_s3(image_url_pf, genre, title)
                    
                    # Insert into database
                    logger.info(f"Inserting album into database: {title} by {artist}...")
                    self.database.insert_entry(title, artist, genre, release_date, reviewer, review_date, image_url_s3)

                    logger.info(f"Saved: {title} - {artist} - {image_url_s3} to database\n")

                page += 1
                time.sleep(1)

    import requests

    # Add some debug logging to see what the API is returning
    def get_album_release_date(self, album_title, artist_name):
        url = "https://musicbrainz.org/ws/2/release/"
        query = f'release:{album_title} AND artist:{artist_name}'
        
        params = {
            "query": query,
            "fmt": "json"
        }

        res = requests.get(url, params=params, headers={"User-Agent": "your-app"})
        data = res.json()

        if data["releases"]:
            # Filter out anniversary/reissue editions and find earliest date
            valid_releases = []
            for release in data["releases"]:
                # Skip if it's marked as anniversary or reissue in disambiguation
                disambiguation = release.get("disambiguation", "").lower()
                if "anniversary" in disambiguation or "remaster" in disambiguation:
                    continue
                
                # Skip bootlegs
                if release.get("status") == "Bootleg":
                    continue
                
                date = release.get("date")
                # Only accept full dates (YYYY-MM-DD format, length 10)
                if date and len(date) == 10:
                    valid_releases.append(date)
            
            # Return the earliest date
            if valid_releases:
                return min(valid_releases)
        
        return None

    def get_album_release_date_ai(self, album_title, artist_name):
        """Use OpenAI to estimate the release date of an album in SQL-friendly format."""
        try:
            prompt = f"""
            What is the release date of the album "{album_title}" by {artist_name}?
            Respond with the date in YYYY-MM-DD format if known, otherwise respond with NULL.
            Do not include any extra text.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a music metadata assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            result = response.choices[0].message.content.strip()

            # Basic validation — must look like YYYY-MM-DD or NULL
            if result.upper() == "NULL":
                return None
            if len(result) == 10 and result[4] == "-" and result[7] == "-":
                return result
            return None

        except Exception as e:
            logger.error(f"❌ OpenAI lookup failed for {album_title}: {e}")
            return None
        
    def parse_review_date(self, date_string):
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            try:
                return datetime.strptime(date_string, "%b %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                logger.info(f"Could not parse date: {date_string}")
                return None
        
    def close(self):
        if self.driver:
            self.driver.quit()
        if self.database:
            self.database.close()

    def audit_database(self):
        """Check database health before fixing anything"""
        
        logger.info("=== DATABASE AUDIT ===\n")
        
        # 1. Total records
        self.database.c.execute("SELECT COUNT(*) FROM albums")
        total = self.database.c.fetchone()[0]
        logger.info(f"📊 Total records: {total:,}")
        
        # 2. Check for duplicates (same title + artist)
        self.database.c.execute("""
            SELECT title, artist, COUNT(*) as count
            FROM albums
            GROUP BY title, artist
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 20
        """)
        duplicates = self.database.c.fetchall()
        
        if duplicates:
            logger.warning(f"\n⚠️  Found {len(duplicates)} duplicate title+artist combinations:")
            for title, artist, count in duplicates[:10]:
                logger.warning(f"  - '{title}' by {artist}: {count} copies")
            
            # Total duplicate records
            self.database.c.execute("""
                SELECT SUM(count - 1) as duplicate_records
                FROM (
                    SELECT COUNT(*) as count
                    FROM albums
                    GROUP BY title, artist
                    HAVING COUNT(*) > 1
                ) dupes
            """)
            dup_count = self.database.c.fetchone()[0]
            logger.warning(f"\n🗑️  Total duplicate records: {dup_count:,}")
        else:
            logger.info("\n✅ No duplicates found")
        
        # 3. Release date quality
        self.database.c.execute("SELECT COUNT(*) FROM albums WHERE release_date IS NULL")
        null_dates = self.database.c.fetchone()[0]
        
        self.database.c.execute("SELECT COUNT(*) FROM albums WHERE release_date > CURRENT_DATE")
        future_dates = self.database.c.fetchone()[0]
        
        self.database.c.execute("SELECT COUNT(*) FROM albums WHERE release_date < '1900-01-01'")
        ancient_dates = self.database.c.fetchone()[0]
        
        logger.info(f"\n📅 Release Date Quality:")
        logger.info(f"  - NULL dates: {null_dates:,}")
        logger.info(f"  - Future dates: {future_dates:,}")
        logger.info(f"  - Pre-1900 dates: {ancient_dates:,}")
        
        # 4. Check for exact duplicates (all fields match)
        self.database.c.execute("""
            SELECT COUNT(*) 
            FROM (
                SELECT title, artist, genre, release_date, reviewer, COUNT(*) as count
                FROM albums
                GROUP BY title, artist, genre, release_date, reviewer
                HAVING COUNT(*) > 1
            ) exact_dupes
        """)
        exact_dupes = self.database.c.fetchone()[0]
        logger.info(f"\n🔍 Exact duplicates (all fields match): {exact_dupes:,}")
        
        # 5. Sample records
        self.database.c.execute("SELECT title, artist, release_date, genre FROM albums LIMIT 5")
        samples = self.database.c.fetchall()
        logger.info(f"\n📝 Sample records:")
        for title, artist, date, genre in samples:
            logger.info(f"  - {title} by {artist} ({date}) [{genre}]")
'''
if __name__ == "__main__":
    # update_db_from_pitchfork()  # Uncomment when needed
    #tweet_anniversaries()
    logger.info(f"Starting the Pitchfork scraper ...")
    scraper = PitchforkScraper()
    try:
        scraper.scrape_all_genres()
    finally:
        scraper.close()  # Always runs, even if crash
    logger.info(f"Begin scraping all genres...")
    logger.info("----------")
    p.scrape_all_genres()
    #p.scroll_down(15)
'''
if __name__ == "__main__":
    scraper = PitchforkScraper()
    
    try:
        scraper.audit_database()  # Run the audit
    finally:
        scraper.close()