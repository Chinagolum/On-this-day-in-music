#!/bin/bash
# ============================================================
#  build_lambdas.sh — Build and deploy all Lambdas
# ============================================================
#  source_code_hash in lambda.tf and consumer.tf detects code
#  changes automatically — no need to force-replace.
# ============================================================
set -e

BUILD_DIR="build"
LAYER_DIR="$BUILD_DIR/layer"
LAYER_REQUIREMENTS="requirements-layer.txt"

echo "🧹 Cleaning old build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

echo "📦 Building Lambda layer..."
mkdir -p "$LAYER_DIR/python"
pip install -r "$LAYER_REQUIREMENTS" -t "$LAYER_DIR/python" --quiet \
  --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.12
cd "$LAYER_DIR"
zip -r "../lambda_layer.zip" python/ --quiet
cd ../..
echo "✅ Lambda layer built"

echo "📦 Building schedule_tweets.zip..."
TEMP=$(mktemp -d)
cp lambdas/daily_tweet_scheduler/schedule_tweets.py "$TEMP/"
cp -r lib "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/schedule_tweets.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ schedule_tweets.zip built"

echo "📦 Building twitter_bot.zip..."
TEMP=$(mktemp -d)
cp lambdas/tweet_poster/create_tweet.py "$TEMP/"
cp -r lib "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/twitter_bot.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ twitter_bot.zip built"

echo "📦 Building telegram_forwarder.zip..."
TEMP=$(mktemp -d)
cp lambdas/telegram_forwarder/forward_to_telegram.py "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/telegram_forwarder.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ telegram_forwarder.zip built"

echo ""
echo "🎉 All builds complete:"
ls -lh "$BUILD_DIR"/*.zip

echo ""
echo "🚀 Deploying to AWS..."
cd terraform
terraform apply -auto-approve
echo "✅ Deployed!"