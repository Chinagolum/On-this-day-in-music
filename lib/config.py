# ------------------------------------------------------------
# Load environment variables from a .env file
# ------------------------------------------------------------

import os
from dotenv import load_dotenv

# Reads key-value pairs from the .env file into environment variables
load_dotenv()


# ------------------------------------------------------------
# Database Configuration
# ------------------------------------------------------------

# PostgreSQL database connection string (e.g., from Supabase)
DB_URL = os.getenv("DB_URL")


# ------------------------------------------------------------
# Twitter API Credentials
# ------------------------------------------------------------

# Used for authenticating requests to the Twitter API
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


# ------------------------------------------------------------
# AWS Configuration
# ------------------------------------------------------------

# S3 bucket and region info for storing album cover images
AWS_BUCKET = os.getenv("AWS_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

# Credentials for programmatic AWS access
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


# ------------------------------------------------------------
# OpenAI API Key
# ------------------------------------------------------------

# Used for generating AI-based tweet content or text completions
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")