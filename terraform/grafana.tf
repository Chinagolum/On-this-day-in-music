# 1. AWS SIDE: Create the Role Grafana will use to "log in" to your AWS
resource "aws_iam_role" "grafana_cloud_read" {
  name = "GrafanaCloudWatchIntegrationRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = { "AWS": "arn:aws:iam::[GRAFANA_ACCOUNT_ID]:root" } 
      Condition = {
        StringEquals = { "sts:ExternalId": "[YOUR_EXTERNAL_ID]" }
      }
    }]
  })
}

# Attach Permissions for both Metrics AND Logs
resource "aws_iam_role_policy_attachment" "metrics_read" {
  role       = aws_iam_role.grafana_cloud_read.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "logs_read" {
  role       = aws_iam_role.grafana_cloud_read.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsReadOnlyAccess"
}

# 2. GRAFANA SIDE: Create the Connection
# Ensure you have the Grafana provider configured in your providers.tf
resource "grafana_data_source" "cloudwatch" {
  type = "cloudwatch"
  name = "AWS-Lambda-Production"

  json_data_encoded = jsonencode({
    defaultRegion = "us-east-1" # Change to your region
    authType      = "arn"
    assumeRoleArn = aws_iam_role.grafana_cloud_read.arn
  })
}
