resource "aws_lambda_function" "schedule_tweets" {
  function_name = "schedule-tweets"           # Cloud name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "schedule_tweets.lambda_handler" # File.Function
  runtime       = "python3.12"
  filename      = "build/schedule_tweets.zip" # New file path
  timeout       = 15 

  environment {
    variables = {
      TWEET_QUEUE_URL = aws_sqs_queue.tweet_queue.url
      DB_URL = var.DB_URL

    }
  }
}

# Updated log group
resource "aws_cloudwatch_log_group" "schedule_tweets_logs" {
  name              = "/aws/lambda/schedule-tweets"
  retention_in_days = 7
}
