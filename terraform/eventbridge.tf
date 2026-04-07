# ---- SCHEDULER: queues all albums at 9am ----
resource "aws_cloudwatch_event_rule" "schedule_tweets_rule" {
  name                = "run-schedule-tweets"
  description         = "Runs the schedule_tweets Lambda every day at 09:00 UTC"
  schedule_expression = "cron(0 9 * * ? *)"
}

resource "aws_cloudwatch_event_target" "schedule_tweets_target" {
  rule      = aws_cloudwatch_event_rule.schedule_tweets_rule.name
  target_id = "schedule-tweets"
  arn       = aws_lambda_function.schedule_tweets.arn
}

resource "aws_lambda_permission" "allow_eventbridge_invoke_schedule_tweets" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.schedule_tweets.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule_tweets_rule.arn
}

# ---- CONSUMER: posts 1 tweet at 10am, 1pm, 4pm ----
resource "aws_cloudwatch_event_rule" "post_tweet_rule" {
  name                = "run-post-tweet"
  description         = "Triggers tweet posting 3x/day, spaced 3 hours apart"
  schedule_expression = "cron(0 10,13,16 * * ? *)"
}

resource "aws_cloudwatch_event_target" "post_tweet_target" {
  rule      = aws_cloudwatch_event_rule.post_tweet_rule.name
  target_id = "post-tweet"
  arn       = aws_lambda_function.twitter_bot.arn
}

resource "aws_lambda_permission" "allow_eventbridge_invoke_twitter_bot" {
  statement_id  = "AllowEventBridgeInvokeTwitterBot"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.twitter_bot.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.post_tweet_rule.arn
}
