#!/bin/bash
# View Lambda logs
# Usage: ./scripts/logs.sh [scheduler|consumer|all] [minutes]
# Examples:
#   ./scripts/logs.sh consumer 10    — last 10 min of consumer logs
#   ./scripts/logs.sh scheduler      — last 5 min of scheduler logs
#   ./scripts/logs.sh                — last 5 min of all logs
REGION="eu-north-1"
TARGET=${1:-all}
MINUTES=${2:-5}

if [ "$TARGET" = "scheduler" ] || [ "$TARGET" = "all" ]; then
  echo "=== 📋 Scheduler Logs (last ${MINUTES}m) ==="
  aws logs tail /aws/lambda/schedule-tweets --region $REGION --since ${MINUTES}m 2>/dev/null || echo "No logs found"
  echo ""
fi

if [ "$TARGET" = "consumer" ] || [ "$TARGET" = "all" ]; then
  echo "=== 🐦 Consumer Logs (last ${MINUTES}m) ==="
  aws logs tail /aws/lambda/twitter-bot-consumer --region $REGION --since ${MINUTES}m 2>/dev/null || echo "No logs found"
fi
