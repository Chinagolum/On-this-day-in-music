# 1. The Main "Live" Queue
resource "aws_sqs_queue" "tweet_queue" {
  name                       = "pitchfork-tweet-queue"
  delay_seconds              = 0
  visibility_timeout_seconds = 90 # 6x Lambda timeout
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tweet_dlq.arn
    maxReceiveCount     = 5 # Moves to DLQ after 5 failed tries
  })
}

# 2. The "Safety Net" Dead Letter Queue
resource "aws_sqs_queue" "tweet_dlq" {
  name = "pitchfork-tweet-dlq"
}
