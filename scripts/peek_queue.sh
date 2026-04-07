#!/bin/bash
# Peek at messages in the queue without consuming them
# Usage: ./scripts/peek_queue.sh [main|dlq]
REGION="eu-north-1"
QUEUE_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-queue"
DLQ_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-dlq"

TARGET=${1:-main}

if [ "$TARGET" = "dlq" ]; then
  URL=$DLQ_URL
  echo "👀 Peeking at Dead Letter Queue..."
else
  URL=$QUEUE_URL
  echo "👀 Peeking at Main Queue..."
fi

aws sqs receive-message \
  --queue-url $URL \
  --region $REGION \
  --visibility-timeout 0 \
  --max-number-of-messages 5 | python3 -m json.tool
