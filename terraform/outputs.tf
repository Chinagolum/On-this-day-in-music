output "tweet_queue_url" {
  value = aws_sqs_queue.tweet_queue.id
}

output "create_tweet_lambda_arn" {
  value = aws_lambda_function.create_tweet.arn
}

output "schedule_tweets_lambda_arn" {
  value = aws_lambda_function.schedule_tweets.arn
}

output "eventbridge_rule_name" {
  value = aws_cloudwatch_event_rule.schedule_tweets_rule.name
}

output "aws_access_key_id" {
  value     = aws_iam_access_key.pitchfork_scraper_key.id
  sensitive = true
}

output "aws_secret_access_key" {
  value     = aws_iam_access_key.pitchfork_scraper_key.secret
  sensitive = true
}
