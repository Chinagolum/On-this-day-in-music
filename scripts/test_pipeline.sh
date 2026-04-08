#!/bin/bash
# Test the full pipeline: queue albums → post one tweet
# Usage: ./scripts/test_pipeline.sh
set -e

REGION="eu-north-1"

echo "📋 Queuing today's albums..."
aws lambda invoke --function-name schedule-tweets --region $REGION output.json && cat output.json
echo ""

echo "🐦 Posting one tweet..."
aws lambda invoke --function-name twitter-bot-consumer --region $REGION test_output.json && cat test_output.json
echo ""

echo "📊 Checking logs..."
sleep 3
aws logs tail /aws/lambda/twitter-bot-consumer --region $REGION --since 2m | grep -E "✅|❌|📸|📥|⚠️|🐦|📭"

rm -f output.json test_output.json
