resource "aws_lambda_function" "schedule_tweets" {
  function_name    = "schedule-tweets"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "schedule_tweets.lambda_handler"
  runtime          = "python3.12"
  filename         = "${path.module}/../build/schedule_tweets.zip"
  timeout          = 15
  source_code_hash = filebase64sha256("${path.module}/../build/schedule_tweets.zip")
  layers           = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      TWEET_QUEUE_URL = aws_sqs_queue.tweet_queue.url
      DB_URL          = var.DB_URL
    }
  }
}

# Log group
resource "aws_cloudwatch_log_group" "schedule_tweets_logs" {
  name              = "/aws/lambda/schedule-tweets"
  retention_in_days = 7
}
