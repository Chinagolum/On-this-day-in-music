#!/bin/bash
# Purge all messages from SQS queues
# Usage: ./scripts/purge_queues.sh
REGION="eu-north-1"
QUEUE_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-queue"
DLQ_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-dlq"

echo "🗑️ Purging main queue..."
aws sqs purge-queue --queue-url $QUEUE_URL --region $REGION
echo "✅ Main queue purged"

echo "🗑️ Purging dead letter queue..."
aws sqs purge-queue --queue-url $DLQ_URL --region $REGION
echo "✅ DLQ purged"
