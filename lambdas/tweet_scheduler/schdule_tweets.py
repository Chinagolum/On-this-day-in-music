import datetime
from lib.db_manager import DatabaseManager

def fetch_todays_albums(event=None):
    """
    Fetch albums whose anniversary is today from the DB.
    Returns a list of album events to send to SQS.
    """
    db = DatabaseManager()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    records = db.fetch_by_release_date(today)
    
    events = []
    # Each record: (id, title, artist, genre, release_date, reviewer, review_date, image_url)
    for record in records:
        _, title, artist, *_ , release_date, *_ = record
        events.append({
            "artist": artist,
            "album": title,
            "release_date": release_date.strftime("%Y-%m-%d") if release_date else None
        })

    db.close()
    return events

# AWS Lambda entrypoint
def lambda_handler(event, context):
    """
    Called by EventBridge daily. Sends album events to SQS.
    """
    import boto3
    import json
    import os

    sqs = boto3.client("sqs")
    queue_url = os.environ["TWEET_QUEUE_URL"]

    album_events = fetch_todays_albums()

    for album_event in album_events:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(album_event)
        )

    return {"status": "queued", "count": len(album_events)}
