# Shared dependency layer
resource "aws_lambda_layer_version" "dependencies" {
  filename            = "${path.module}/../build/lambda_layer.zip"
  layer_name          = "pitchfork-dependencies"
  compatible_runtimes = ["python3.12"]
  description         = "Shared deps: psycopg2, tweepy, aws-embedded-metrics, openai"
  source_code_hash    = filebase64sha256("${path.module}/../build/lambda_layer.zip")
}

resource "aws_lambda_function" "twitter_bot" {
  function_name    = "twitter-bot-consumer"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "create_tweet.lambda_handler"
  runtime          = "python3.12"
  filename         = "${path.module}/../build/twitter_bot.zip"
  timeout          = 60
  source_code_hash = filebase64sha256("${path.module}/../build/twitter_bot.zip")
  layers           = [aws_lambda_layer_version.dependencies.arn]

  environment {
    variables = {
      TWITTER_API_KEY       = var.TWITTER_API_KEY
      TWITTER_API_SECRET    = var.TWITTER_API_SECRET
      TWITTER_ACCESS_TOKEN  = var.TWITTER_ACCESS_TOKEN
      TWITTER_ACCESS_SECRET = var.TWITTER_ACCESS_SECRET
      TWEET_QUEUE_URL       = aws_sqs_queue.tweet_queue.url
      GROQ_API_KEY          = var.GROQ_API_KEY
    }
  }
}

# CloudWatch log group
resource "aws_cloudwatch_log_group" "twitter_bot_logs" {
  name              = "/aws/lambda/twitter-bot-consumer"
  retention_in_days = 7
}
