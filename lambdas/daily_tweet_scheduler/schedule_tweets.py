import datetime
from lib.db_manager import DatabaseManager
from aws_embedded_metrics import metric_scope

@metric_scope
def lambda_handler(event, context, metrics):
    """
    Called by EventBridge daily. Purges stale messages, then queues today's albums.
    """
    import boto3
    import json
    import os

    metrics.set_namespace("OnThisDayInMusic")
    metrics.set_dimensions({"Service": "ScheduleTweets"})
    metrics.put_metric("Invocations", 1, "Count")

    sqs = boto3.client("sqs")
    queue_url = os.environ["TWEET_QUEUE_URL"]

    try:
        # Purge yesterday's leftovers
        print("🧹 Purging stale messages...")
        sqs.purge_queue(QueueUrl=queue_url)
        print("✅ Queue purged")

        db = DatabaseManager()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        records = db.fetch_by_release_date(today)
        
        events = []
        # Each record: (id, title, artist, genre, release_date, reviewer, review_date, image_url)
        for record in records:
            title = record[1]
            artist = record[2]
            release_date = record[4]
            image_url = record[7]

            events.append({
                "artist": artist,
                "album": title,
                "release_date": release_date.strftime("%Y-%m-%d") if release_date else None,
                "image_url": image_url
            })

        db.close()
        
        # Send to SQS
        for album_event in events:
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(album_event)
            )
        
        metrics.put_metric("AlbumsQueued", len(events), "Count")
        metrics.put_metric("Success", 1, "Count")
        
        print(f"✅ Queued {len(events)} albums")
        
        return {"status": "queued", "count": len(events)}
        
    except Exception as e:
        metrics.put_metric("Errors", 1, "Count")
        print(f"❌ Error: {e}")
        raise