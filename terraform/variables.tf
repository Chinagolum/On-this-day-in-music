variable "OPENAI_API_KEY" {
  description = "OpenAI API key for the scraper"
  type        = string
  sensitive   = true
}

variable "AWS_REGION" {
  description = "AWS region to deploy resources"
  type        = string
}

variable "AWS_ACCESS_KEY_ID" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}

variable "DB_URL" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "subnets" {
  description = "List of subnet IDs for the ECS service"
  type        = list(string)
}

variable "security_group" {
  description = "Security group ID for the ECS service"
  type        = string
}

variable "TWITTER_API_KEY" {
  description = "API key for Twitter"
  type        = string
  sensitive   = true
}

variable "TWITTER_ACCESS_SECRET" {
  description = "Access secret for Twitter"
  type        = string
  sensitive   = true
}

variable "TWITTER_API_SECRET" {
  description = "Twitter API secret key"
  type        = string
  sensitive   = true
}

variable "AWS_BUCKET" {
  description = "S3 bucket for album covers"
  type        = string
}

variable "TWITTER_ACCESS_TOKEN" {
  description = "Twitter API access token"
  type        = string
  sensitive   = true
}
