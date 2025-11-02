# --- Create Tweet Lambda (triggered by SQS)
resource "aws_lambda_function" "create_tweet" {
  function_name = "create-tweet"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "create_tweet.lambda_handler"
  runtime       = "python3.12"
  filename      = "build/create_tweet.zip"

  environment {
    variables = {
      TWEET_QUEUE_URL = aws_sqs_queue.tweet_queue.id
    }
  }
}

# --- Schedule Tweets Lambda (fills SQS)
resource "aws_lambda_function" "schedule_tweets" {
  function_name = "schedule-tweets"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "schedule_tweets.lambda_handler"
  runtime       = "python3.12"
  filename      = "build/schedule_tweets.zip"

  environment {
    variables = {
      TWEET_QUEUE_URL = aws_sqs_queue.tweet_queue.id
    }
  }
}

# Connect SQS → create tweet Lambda
resource "aws_lambda_event_source_mapping" "create_tweet_trigger" {
  event_source_arn = aws_sqs_queue.tweet_queue.arn
  function_name    = aws_lambda_function.create_tweet.arn
  batch_size       = 1
  enabled          = true
}
