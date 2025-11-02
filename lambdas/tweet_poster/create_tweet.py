from lib.twitter_bot import TwitterBot

def handle_tweet_request(event):
    """
    Expects event = {
        "artist": "Artist Name",
        "album": "Album Name",
        "release_date": "YYYY-MM-DD"
    }
    """
    artist = event.get("artist")
    album = event.get("album")
    release_date = event.get("release_date")

    if not all([artist, album, release_date]):
        return {"status": "failed", "error": "Missing required fields in event."}

    twitter = TwitterBot()
    try:
        msg = twitter.post_album_anniversary(artist, album, release_date)
        return {"status": "tweeted", "message": msg}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

# AWS Lambda entrypoint
def lambda_handler(event, context):
    return handle_tweet_request(event)
