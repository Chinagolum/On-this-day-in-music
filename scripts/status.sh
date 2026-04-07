#!/bin/bash
# Check the health of the entire system
# Usage: ./scripts/status.sh
REGION="eu-north-1"
QUEUE_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-queue"
DLQ_URL="https://sqs.eu-north-1.amazonaws.com/846693397697/pitchfork-tweet-dlq"

echo "=== 🎼 On This Day in Music — System Status ==="
echo ""

echo "📋 SQS Queue:"
MAIN_COUNT=$(aws sqs get-queue-attributes --queue-url $QUEUE_URL --attribute-names ApproximateNumberOfMessages --region $REGION --query 'Attributes.ApproximateNumberOfMessages' --output text)
DLQ_COUNT=$(aws sqs get-queue-attributes --queue-url $DLQ_URL --attribute-names ApproximateNumberOfMessages --region $REGION --query 'Attributes.ApproximateNumberOfMessages' --output text)
echo "  Main queue: $MAIN_COUNT messages"
echo "  Dead letter queue: $DLQ_COUNT messages"
echo ""

echo "⚙️ Lambda Functions:"
for FUNC in schedule-tweets twitter-bot-consumer; do
  STATUS=$(aws lambda get-function-configuration --function-name $FUNC --region $REGION --query '[LastUpdateStatus, Handler, Runtime]' --output text)
  echo "  $FUNC: $STATUS"
done
echo ""

echo "📅 EventBridge Rules:"
for RULE in run-schedule-tweets run-post-tweet; do
  STATE=$(aws events describe-rule --name $RULE --region $REGION --query '[State, ScheduleExpression]' --output text 2>/dev/null || echo "NOT FOUND")
  echo "  $RULE: $STATE"
done
echo ""

echo "📊 Recent Consumer Logs (last 30 min):"
aws logs tail /aws/lambda/twitter-bot-consumer --region $REGION --since 30m 2>/dev/null | grep -E "✅|❌|📸|📭|🐦" | tail -10 || echo "  No recent logs"
echo ""

echo "📊 Recent Scheduler Logs (last 30 min):"
aws logs tail /aws/lambda/schedule-tweets --region $REGION --since 30m 2>/dev/null | grep -E "✅|❌|Queued" | tail -5 || echo "  No recent logs"
