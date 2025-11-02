import tweepy
from config import *

class TwitterBot:
    def __init__(self):
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        self.api = tweepy.API(auth)

    def post_album_anniversary(self, artist, album, release_date):
        try:
            year_diff = datetime.datetime.now().year - int(release_date[:4])
            message = f"On this day {year_diff} years ago, {artist} released \"{album}\" ({release_date}) 🎶"
            self.api.update_status(message)
        except Exception as e:
            print(f"Error posting tweet: {e}")
