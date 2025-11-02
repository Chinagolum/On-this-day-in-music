from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import time
import lxml
from bs4 import BeautifulSoup
import boto3
from urllib.parse import urlparse, unquote
import os
from lib.config import *
from lib.db_manager import DatabaseManager
from openai import OpenAI



# ---------- Configure AWS ----------


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

class PitchforkScraper:
    def __init__(self):

        options = Options()
        options.binary_location = "/usr/bin/chromium"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/chromedriver")

        self.driver = webdriver.Chrome(service=service, options=options)
        self.genres = ["rap", "rock", "pop", "jazz", "electronic", "metal", "folk", "experimental"]
        print("Connecting to database...")
        self.database = DatabaseManager()
        print("Initializing OpenAI client...")
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    def scroll_down(self, times):
        body = self.driver.find_element("tag name", "body")
        for _ in range(times):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
    
    def upload_image_to_s3(self, image_url, genre, title):
        try:
            print(f"Uploading image for {title} from {image_url}...")
            response = requests.get(image_url)
            print(f"Image download response code: {response.status_code}")
            response.raise_for_status()

            # Create safe filename using genre + title
            ext = os.path.splitext(urlparse(image_url).path)[1] or ".jpg"
            filename = f"{title.replace('/', '_')}{ext}"
            s3_key = f"{genre}/{filename}"

            print(f"Uploading to S3 bucket {AWS_BUCKET} with key {s3_key}...")
            s3.put_object(
                Bucket=AWS_BUCKET,
                Key=s3_key,
                Body=response.content,
                ContentType="image/jpeg",
            )

            return f"https://{AWS_BUCKET}.s3.amazonaws.com/{s3_key}"
        except Exception as e:
            print(f"❌ Failed to upload {title}: {e}")
            return None

    def scrape_all_genres(self):
        for genre in self.genres:
            print(f"\nScraping genre: {genre}")
            page = 1
            while True:
                url = f"https://pitchfork.com/genre/{genre}/review/?page={page}"
                print(f"\nOpening: {url}")
                self.driver.get(url)
                time.sleep(5)

                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                albums = soup.find_all('div', attrs={'data-item': True, 'role': 'button'})

                if not albums:
                    print("No albums found — likely a blank page. Stopping.")
                    break

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
                    review_date = review_date_tag.get_text(strip=True)
                    image_url_pf = image_url_tag.get('src') or image_url_tag.get('data-src')

                    # Upload image to S3
                    print(f"Uploading image for album: {title} by {artist} to S3...")
                    image_url_s3 = self.upload_image_to_s3(image_url_pf, genre, title)

                    if image_url_s3 is None:
                        return
                    # Insert into database
                    print(f"Inserting album into database: {title} by {artist}...")
                    self.database.insert_entry(title, artist, genre, release_date, reviewer, review_date, image_url_s3)

                    print(f"Saved: {title} - {artist} - {image_url_s3} to database\n")

                page += 1
                time.sleep(1)
                if page > 3:  # Temporary stop for testing
                    break

    def get_album_release_date(self, album_title, artist_name):
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
            print(f"❌ OpenAI lookup failed for {album_title}: {e}")
            return None
  
if __name__ == "__main__":
    # update_db_from_pitchfork()  # Uncomment when needed
    #tweet_anniversaries()
    print(f"Starting scraper...")
    p = PitchforkScraper()
    print(f"Scraping all genres...")
    print("----------")
    p.scrape_all_genres()
    #p.scroll_down(15)
