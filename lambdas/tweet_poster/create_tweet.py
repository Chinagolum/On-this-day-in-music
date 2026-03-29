import json
from lib.twitter_bot import TwitterBot
from aws_embedded_metrics import metric_scope

twitter = TwitterBot()

@metric_scope
def lambda_handler(event, context, metrics):
    """
    AWS Lambda entrypoint triggered by SQS.
    """
    metrics.set_namespace("OnThisDayInMusic")
    metrics.set_dimensions({"Service": "TwitterBot"})
    metrics.put_metric("Invocations", 1, "Count")
    
    results = []
    tweets_posted = 0
    errors = 0
    
    for record in event.get('Records', []):
        try:
            data = json.loads(record['body'])
            
            artist = data.get("artist")
            album = data.get("album")
            release_date = data.get("release_date")

            if not all([artist, album, release_date]):
                metrics.put_metric("ValidationErrors", 1, "Count")
                errors += 1
                continue

            msg = twitter.post_album_anniversary(artist, album, release_date)
            results.append({"status": "tweeted", "message": msg})
            tweets_posted += 1
            
        except Exception as e:
            errors += 1
            print(f"❌ Error processing message: {e}")
            raise e
    
    metrics.put_metric("TweetsPosted", tweets_posted, "Count")
    if errors > 0:
        metrics.put_metric("Errors", errors, "Count")

    print(f"✅ Posted {tweets_posted} tweets")

    return {
        "statusCode": 200,
        "results": results
    }