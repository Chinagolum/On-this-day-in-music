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
