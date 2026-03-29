resource "aws_lambda_function" "twitter_bot" {
  function_name = "twitter-bot-consumer"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "twitter_bot.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.module}/../build/twitter_bot.zip"

  environment {
    variables = {
      # Ensure these are defined in your variables.tf
      TWITTER_API_KEY    = var.TWITTER_API_KEY
      TWITTER_API_SECRET = var.TWITTER_API_SECRET
      TWITTER_ACCESS_TOKEN = var.TWITTER_ACCESS_TOKEN
      TWITTER_ACCESS_SECRET = var.TWITTER_ACCESS_SECRET
    }
  }
}

# Link SQS to this Lambda
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.tweet_queue.arn
  function_name    = aws_lambda_function.twitter_bot.arn
  batch_size       = 1 # Process 1 message per invocation for clean error handling
  enabled          = true
}
