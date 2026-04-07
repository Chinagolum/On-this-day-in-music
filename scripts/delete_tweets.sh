#!/bin/bash
# Delete tweets by ID
# Usage: ./scripts/delete_tweets.sh <tweet_id> [tweet_id2] [tweet_id3] ...
# Example: ./scripts/delete_tweets.sh 2041283931866091685 2041287838663111141
set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/delete_tweets.sh <tweet_id> [tweet_id2] ..."
  echo "Example: ./scripts/delete_tweets.sh 2041283931866091685"
  exit 1
fi

TWEET_IDS=""
for id in "$@"; do
  TWEET_IDS="$TWEET_IDS    client.delete_tweet($id); print(f'🗑️ Deleted: $id')\n"
done

python3 -c "
import tweepy, os
from dotenv import load_dotenv
load_dotenv()
client = tweepy.Client(
    consumer_key=os.getenv('TWITTER_API_KEY'),
    consumer_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
)
$(echo -e "$TWEET_IDS")
print('✅ Done')
"
