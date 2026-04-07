import tweepy
import boto3
import tempfile
import os
from urllib.parse import urlparse, unquote
from lib.config import *
import datetime

class TwitterBot:
    def __init__(self):
        # v2 client for posting tweets
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )

        # v1.1 auth for media uploads (v2 doesn't support media upload)
        auth = tweepy.OAuth1UserHandler(
            TWITTER_API_KEY,
            TWITTER_API_SECRET,
            TWITTER_ACCESS_TOKEN,
            TWITTER_ACCESS_SECRET
        )
        self.api = tweepy.API(auth)
        self.s3 = boto3.client("s3")

    def upload_image(self, image_url):
        """
        Download image from S3 and upload to Twitter.
        Returns the media_id or None if it fails.
        """
        try:
            # Parse S3 URL to get bucket and key
            # URL format: https://album-covers-3543.s3.eu-north-1.amazonaws.com/genre/title.jpg
            parsed = urlparse(image_url)
            hostname = parsed.hostname
            bucket = hostname.split(".")[0]
            key = unquote(parsed.path.lstrip("/"))

            print(f"📥 Downloading from S3: bucket={bucket}, key={key}")

            # Download from S3 to temp file
            ext = os.path.splitext(key)[1] or ".jpg"
            tmp_path = tempfile.mktemp(suffix=ext)
            self.s3.download_file(bucket, key, tmp_path)

            # Upload to Twitter
            media = self.api.media_upload(filename=tmp_path)
            os.unlink(tmp_path)

            print(f"📸 Image uploaded: media_id={media.media_id}")
            return media.media_id

        except Exception as e:
            print(f"⚠️ Image upload failed: {e}")
            return None

    def post_album_anniversary(self, artist, album, release_date, image_url=None):
        try:
            import random
            emojis = ["🎶", "🎵", "🎼", "🎧", "🎸", "🎹", "🎷", "🎺", "🥁", "🎤", "📀", "💿", "🔊", "🎻", "🪗", "🎙️", "🌀", "✨", "🔥", "💫", "⚡", "🫧", "🪩"]
            emoji = random.choice(emojis)
            year_diff = datetime.datetime.now().year - int(release_date[:4])
            message = f"On this day {year_diff} years ago, {artist} released \"{album}\" ({release_date}) {emoji}"

            # Upload image if available
            media_ids = None
            if image_url:
                media_id = self.upload_image(image_url)
                if media_id:
                    media_ids = [media_id]

            response = self.client.create_tweet(text=message, media_ids=media_ids)
            return f"Tweet posted: {response.data['id']}"
        except Exception as e:
            print(f"Error posting tweet: {e}")
            raise