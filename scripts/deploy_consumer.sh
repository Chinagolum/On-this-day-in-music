#!/bin/bash
set -e

# 1. Clean build environment
rm -rf build/package
mkdir -p build/package

# 2. Install Linux-compatible dependencies
pip install \
    --platform manylinux2014_x86_64 \
    --target build/package \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    tweepy python-dotenv aws-embedded-metrics

# 3. Copy code
cp lambdas/tweet_poster/create_tweet.py build/package/
cp -r lib build/package/

# 4. Zip and Deploy
cd build/package && zip -r ../twitter_bot.zip . && cd ../..
aws lambda update-function-code --function-name twitter-bot-consumer --zip-file fileb://build/twitter_bot.zip

echo "✅ Consumer deployed!"