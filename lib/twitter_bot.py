import tweepy
from lib.config import *
import datetime

class TwitterBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )      

    def post_album_anniversary(self, artist, album, release_date):
        try:
            year_diff = datetime.datetime.now().year - int(release_date[:4])
            message = f"On this day {year_diff} years ago, {artist} released \"{album}\" ({release_date}) 🎶"
            self.client.create_tweet(text=message)
        except Exception as e:
            print(f"Error posting tweet: {e}")