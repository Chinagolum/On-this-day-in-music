#!/bin/bash

# Clean up old zips
rm -f build/*.zip

# Ensure build folder exists
mkdir -p build

echo "Building Lambda zips..."

# Zip create_tweet Lambda
zip -j build/create_tweet.zip lambdas/tweet_poster/create_tweet.py
echo "Created build/create_tweet.zip"

# Zip schedule_tweets Lambda
zip -j build/schedule_tweets.zip lambdas/daily_tweet_scheduler/schedule_tweets.py
echo "Created build/schedule_tweets.zip"

echo "All Lambdas built successfully!"
