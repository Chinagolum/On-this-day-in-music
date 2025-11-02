resource "aws_sqs_queue" "tweet_queue" {
  name                      = "pitchfork-tweet-queue"
  delay_seconds             = 0
  visibility_timeout_seconds = 60
  message_retention_seconds  = 86400 # 1 day
}

resource "aws_sqs_queue" "tweet_dlq" {
  name = "pitchfork-tweet-dlq"
}

resource "aws_sqs_queue_redrive_policy" "tweet_redrive" {
  queue_url = aws_sqs_queue.tweet_queue.id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tweet_dlq.arn
    maxReceiveCount     = 3
  })
}
