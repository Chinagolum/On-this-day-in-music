# Use existing IAM user (imported or already in state)
resource "aws_iam_user" "pitchfork_scraper" {
  name = "pitchfork-scraper"
}

# Use existing IAM access key
resource "aws_iam_access_key" "pitchfork_scraper_key" {
  user = aws_iam_user.pitchfork_scraper.name
}

# IAM policy for S3 access
resource "aws_iam_policy" "pitchfork_s3_policy" {
  name        = "pitchfork-s3-policy"
  description = "Policy for the pitchfork scraper S3 access"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:ListBucket", "s3:GetObject", "s3:PutObject"]
        Effect   = "Allow"
        Resource = ["arn:aws:s3:::album-covers-3543", "arn:aws:s3:::album-covers-3543/*"]
      }
    ]
  })
}

# Attach the policy to the user
resource "aws_iam_user_policy_attachment" "pitchfork_scraper_attachment" {
  user       = aws_iam_user.pitchfork_scraper.name
  policy_arn = aws_iam_policy.pitchfork_s3_policy.arn
}
