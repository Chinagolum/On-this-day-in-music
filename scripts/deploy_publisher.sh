#!/bin/bash
set -e # Stop script if any command fails

echo "🚀 Starting clean local deployment..."

# 1. Clean workspace
rm -rf build/package deploy.zip
mkdir -p build/package

# 2. Bundle Linux-compatible dependencies
echo "📦 Installing Linux dependencies..."
pip install \
    --platform manylinux2014_x86_64 \
    --target build/package \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    psycopg2-binary aws-embedded-metrics

# 3. Copy code
echo "📂 Copying application code..."
cp lambdas/daily_tweet_scheduler/schedule_tweets.py build/package/
cp -r lib build/package/

# 4. Create Package
echo "🤐 Creating zip archive..."
cd build/package && zip -r ../../deploy.zip . && cd ../..

# 5. Upload to AWS
echo "☁️  Uploading to AWS Lambda..."
aws lambda update-function-code \
  --function-name schedule-tweets \
  --zip-file fileb://deploy.zip

echo "✅ Success! Deployment complete."