#!/bin/bash
# ============================================================
#  build_lambdas.sh — Package all Lambda functions + layer
# ============================================================
#  Usage:  ./build_lambdas.sh
#  Output: build/
#            ├── lambda_layer.zip        (shared dependencies)
#            ├── schedule_tweets.zip     (scheduler Lambda)
#            ├── twitter_bot.zip         (tweet poster Lambda)
#            └── telegram_forwarder.zip  (Telegram alerts Lambda)
# ============================================================

set -e  # Exit on any error

# -- Config --
BUILD_DIR="build"
LAYER_DIR="$BUILD_DIR/layer"
LAYER_REQUIREMENTS="requirements-layer.txt"

echo "🧹 Cleaning old build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# ============================================================
# 1. BUILD THE LAMBDA LAYER (shared dependencies for Linux)
# ============================================================
echo "📦 Building Lambda layer..."
mkdir -p "$LAYER_DIR/python"
pip install -r "$LAYER_REQUIREMENTS" -t "$LAYER_DIR/python" --quiet \
  --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.12
cd "$LAYER_DIR"
zip -r "../lambda_layer.zip" python/ --quiet
cd ../..
echo "✅ Lambda layer built"

# ============================================================
# 2. BUILD schedule_tweets.zip
# ============================================================
echo "📦 Building schedule_tweets.zip..."
TEMP=$(mktemp -d)
cp lambdas/daily_tweet_scheduler/schedule_tweets.py "$TEMP/"
cp -r lib "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/schedule_tweets.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ schedule_tweets.zip built"

# ============================================================
# 3. BUILD twitter_bot.zip (tweet poster consumer)
# ============================================================
echo "📦 Building twitter_bot.zip..."
TEMP=$(mktemp -d)
cp lambdas/tweet_poster/create_tweet.py "$TEMP/"
cp -r lib "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/twitter_bot.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ twitter_bot.zip built"

# ============================================================
# 4. BUILD telegram_forwarder.zip
# ============================================================
echo "📦 Building telegram_forwarder.zip..."
TEMP=$(mktemp -d)
cp lambdas/telegram_forwarder/forward_to_telegram.py "$TEMP/"
cd "$TEMP"
zip -r "$OLDPWD/$BUILD_DIR/telegram_forwarder.zip" . --quiet
cd "$OLDPWD"
rm -rf "$TEMP"
echo "✅ telegram_forwarder.zip built"

# ============================================================
# 5. DEPLOY TO AWS
# ============================================================
echo ""
echo "🎉 All builds complete:"
ls -lh "$BUILD_DIR"/*.zip

echo ""
echo "🚀 Deploying to AWS..."
cd terraform
terraform apply -auto-approve
echo "✅ Deployed!"