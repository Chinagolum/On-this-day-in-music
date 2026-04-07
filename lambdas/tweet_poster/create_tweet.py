import json
import boto3
import os
from openai import OpenAI
from lib.twitter_bot import TwitterBot
from aws_embedded_metrics import metric_scope

twitter = TwitterBot()
sqs = boto3.client("sqs")

# Groq uses the OpenAI SDK — just change the base URL
groq_client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def verify_album(artist, album, release_date):
    """
    Use Groq (Llama) to verify if the album, artist, and release date are correct.
    Returns (True, reason) if valid, (False, reason) if not.
    """
    try:
        prompt = f"""Verify if the following music album information is accurate:
- Artist: {artist}
- Album: {album}
- Release Date: {release_date}

Check:
1. Did this artist actually release this album?
2. Is the release date correct (month and day matter most)?

Respond with ONLY a JSON object, no markdown, no backticks:
{{"valid": true/false, "reason": "brief explanation"}}"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a music metadata fact-checker. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(result)
        return parsed.get("valid", False), parsed.get("reason", "No reason given")

    except Exception as e:
        print(f"⚠️ AI verification failed: {e}")
        # If AI fails, let it through rather than blocking everything
        return True, f"Verification skipped due to error: {e}"


@metric_scope
def lambda_handler(event, context, metrics):
    """
    Called by EventBridge 3x/day.
    Pulls messages from SQS, verifies with AI, tweets the first valid one.
    """
    metrics.set_namespace("OnThisDayInMusic")
    metrics.set_dimensions({"Service": "TwitterBot"})
    metrics.put_metric("Invocations", 1, "Count")

    queue_url = os.environ["TWEET_QUEUE_URL"]
    verified = 0
    rejected = 0

    while True:
        # Pull 1 message
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5
        )

        messages = response.get("Messages", [])

        if not messages:
            print(f"📭 Queue empty. Verified: {verified}, Rejected: {rejected}")
            metrics.put_metric("TweetsPosted", 0, "Count")
            metrics.put_metric("AlbumsRejected", rejected, "Count")
            return {
                "statusCode": 200,
                "result": "no valid messages found",
                "rejected": rejected
            }

        message = messages[0]

        try:
            data = json.loads(message["Body"])
            artist = data.get("artist")
            album = data.get("album")
            release_date = data.get("release_date")
            image_url = data.get("image_url")

            if not all([artist, album, release_date, image_url]):
                print(f"⚠️ Missing fields or no cover, skipping: {album} by {artist}")
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
                rejected += 1
                continue

            # AI verification
            is_valid, reason = verify_album(artist, album, release_date)

            if not is_valid:
                print(f"❌ Rejected: {album} by {artist} — {reason}")
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])
                metrics.put_metric("AlbumsRejected", 1, "Count")
                rejected += 1
                continue

            # Passed verification — tweet it with album cover
            print(f"✅ Verified: {album} by {artist} — {reason}")
            msg = twitter.post_album_anniversary(artist, album, release_date, image_url)
            print(f"🐦 {msg}")

            sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"])

            metrics.put_metric("TweetsPosted", 1, "Count")
            metrics.put_metric("AlbumsVerified", 1, "Count")
            metrics.put_metric("AlbumsRejected", rejected, "Count")

            return {
                "statusCode": 200,
                "result": "tweeted",
                "message": msg,
                "artist": artist,
                "album": album,
                "verified_reason": reason,
                "rejected_before_success": rejected
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            metrics.put_metric("Errors", 1, "Count")
            # Don't delete — let it retry or go to DLQ
            raise
