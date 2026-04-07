# 🎼 On This Day in Music

A fully automated Twitter bot that tweets album anniversaries daily — powered by AWS, AI verification, and album cover art.

Every day, the bot checks which albums were released on today's date, verifies the data using AI, and posts beautifully formatted tweets with album artwork. Three tweets per day, spaced three hours apart.

---

## How It Works

The system follows a producer-consumer architecture built on AWS serverless services:

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐     ┌─────────────┐     ┌─────────┐
│ EventBridge │────▶│  Scheduler   │────▶│    SQS    │────▶│  Consumer   │────▶│ Twitter │
│  (9am UTC)  │     │   Lambda     │     │   Queue   │     │   Lambda    │     │   API   │
└─────────────┘     └──────────────┘     └───────────┘     └─────────────┘     └─────────┘
                          │                                       │
                          ▼                                       ▼
                    ┌───────────┐                          ┌─────────────┐
                    │ Supabase  │                          │  Groq AI    │
                    │ Postgres  │                          │ Verification│
                    └───────────┘                          └─────────────┘
                                                                 │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │  S3 Album   │
                                                          │   Covers    │
                                                          └─────────────┘
```

**9:00 UTC** — EventBridge triggers the **Scheduler Lambda**, which queries the Supabase database for all albums released on today's month and day. It queues every match (typically 10–20 albums) into SQS, including the S3 album cover URL.

**10:00, 13:00, 16:00 UTC** — EventBridge triggers the **Consumer Lambda** three times. Each invocation pulls one message from the queue, sends the album metadata to **Groq AI** (Llama 3.3 70B) for fact-checking, and if verified, downloads the album cover from **S3** and posts a tweet with the image attached. If verification fails, the message is discarded and the next one is tried until a valid album is found.

**End of day** — Any remaining messages in the queue expire automatically after 24 hours. Failed messages (after 5 retries) land in a Dead Letter Queue for debugging.

---

## Project Structure

```
On-this-day-in-music/
│
├── lib/                              # Shared library code
│   ├── config.py                     # Environment variable loader
│   ├── db_manager.py                 # PostgreSQL database operations
│   ├── twitter_bot.py                # Tweet posting + image upload
│   ├── pitchfork_scraper.py          # Web scraper for album data
│   └── __init__.py
│
├── lambdas/                          # AWS Lambda handlers
│   ├── daily_tweet_scheduler/
│   │   └── schedule_tweets.py        # Queries DB, queues albums to SQS
│   ├── tweet_poster/
│   │   └── create_tweet.py           # Pulls from SQS, verifies with AI, tweets
│   └── telegram_forwarder/
│       └── forward_to_telegram.py    # Forwards SNS alerts to Telegram
│
├── terraform/                        # Infrastructure as Code
│   ├── provider.tf                   # AWS provider config
│   ├── variables.tf                  # Variable declarations
│   ├── lambda.tf                     # Scheduler Lambda resource
│   ├── consumer.tf                   # Consumer Lambda + dependency layer
│   ├── eventbridge.tf                # Cron schedules (9am, 10am, 1pm, 4pm)
│   ├── sqs.tf                        # Tweet queue + Dead Letter Queue
│   ├── iam_lambda.tf                 # Lambda permissions (logs, SQS, S3)
│   ├── iam_s3.tf                     # S3 access for scraper
│   ├── pitchfork_scraper.tf          # ECS Fargate scraper service
│   └── outputs.tf                    # Exported values
│
├── scripts/                          # Utility scripts
│   ├── build_lambdas.sh              # Build + deploy everything
│   ├── test_pipeline.sh              # Test the full pipeline end-to-end
│   ├── status.sh                     # Check system health
│   ├── logs.sh                       # View Lambda logs
│   ├── run_tests.sh                  # Run the test suite
│   ├── peek_queue.sh                 # Inspect queue messages
│   ├── purge_queues.sh               # Clear all queue messages
│   ├── delete_tweets.sh              # Delete tweets by ID
│   └── audit_db.sh                   # Run database health check
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Shared fixtures (mock env, SQS, DB)
│   ├── test_db_manager.py            # Database operation tests
│   ├── test_twitter_bot.py           # Tweet posting tests
│   ├── test_create_tweet.py          # Consumer Lambda tests
│   ├── test_schedule_tweets.py       # Scheduler Lambda tests
│   └── test_pitchfork_scraper.py     # Scraper tests
│
├── requirements-layer.txt            # Lambda layer dependencies
├── alert-no-tweets.json              # Grafana alert definition
└── README.md
```

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Database** | Supabase (PostgreSQL) | Stores album metadata (title, artist, genre, release date, cover URL) |
| **Scheduler** | AWS Lambda + EventBridge | Queries DB daily and queues album anniversaries |
| **Queue** | AWS SQS + DLQ | Decouples scheduling from posting, handles retries |
| **Consumer** | AWS Lambda + EventBridge | Posts one verified tweet per invocation, 3x daily |
| **AI Verification** | Groq (Llama 3.3 70B) | Fact-checks album name, artist, and release date before tweeting |
| **Image Storage** | AWS S3 | Stores scraped album cover artwork |
| **Posting** | Twitter/X API v2 + v1.1 | Posts tweets (v2) and uploads media (v1.1) |
| **Scraper** | ECS Fargate + Selenium | Scrapes Pitchfork reviews and stores album data |
| **Monitoring** | Grafana Cloud + CloudWatch | Dashboard for queue depth, tweets posted, errors, Lambda duration |
| **Alerting** | Grafana + SNS + Telegram | Sends alert if no tweets are posted in a day |
| **Infrastructure** | Terraform | All AWS resources defined as code |

---

## Setup

### Prerequisites

- **AWS Account** with CLI configured (`aws configure`)
- **Supabase** project with a PostgreSQL database
- **Twitter/X Developer Account** with API v2 access and pay-per-use credits
- **Groq Account** at [console.groq.com](https://console.groq.com) (free tier)
- **Terraform** installed (>= 1.5.0)
- **Python 3.12**

### 1. Clone and Configure

```bash
git clone https://github.com/your-username/On-this-day-in-music.git
cd On-this-day-in-music
```

Create `terraform/terraform.tfvars` with your credentials:

```hcl
DB_URL                = "postgresql://user:pass@host:5432/db"
TWITTER_API_KEY       = "your-key"
TWITTER_API_SECRET    = "your-secret"
TWITTER_ACCESS_TOKEN  = "your-token"
TWITTER_ACCESS_SECRET = "your-access-secret"
GROQ_API_KEY          = "your-groq-key"
AWS_ACCESS_KEY_ID     = "your-aws-key"
AWS_SECRET_ACCESS_KEY = "your-aws-secret"
AWS_REGION            = "eu-north-1"
AWS_BUCKET            = "your-album-covers-bucket"
OPENAI_API_KEY        = "your-openai-key"
subnets               = ["subnet-xxx", "subnet-yyy"]
security_group        = "sg-xxx"
```

> **Security**: Never commit `terraform.tfvars` to version control. Add it to `.gitignore`.

### 2. Build and Deploy

```bash
chmod +x scripts/*.sh
./scripts/build_lambdas.sh
```

This single command packages all Lambda functions with Linux-compatible dependencies, creates a shared Lambda layer, and deploys everything to AWS via Terraform.

### 3. Populate the Database

Run the Pitchfork scraper to populate your database with album data:

```bash
python3 -c "
from lib.pitchfork_scraper import PitchforkScraper
s = PitchforkScraper()
s.scrape_all_genres()
s.close()
"
```

### 4. Verify

```bash
./scripts/test_pipeline.sh
```

---

## Scripts Reference

All scripts live in the `scripts/` directory. Make them executable once with `chmod +x scripts/*.sh`.

### Building & Deploying

| Script | Description |
|---|---|
| `./scripts/build_lambdas.sh` | Packages all Lambdas, builds the dependency layer with Linux binaries, and deploys to AWS via Terraform. This is the only command you need for deployments. |

### Testing

| Script | Description |
|---|---|
| `./scripts/test_pipeline.sh` | Runs the full pipeline end-to-end: queues today's albums, posts one tweet, and shows the logs. Use this to verify everything works after a deploy. |
| `./scripts/run_tests.sh` | Runs the pytest test suite. Pass a test file name to run a specific file: `./scripts/run_tests.sh test_create_tweet` |
| `./scripts/run_tests.sh test_db_manager -v` | Run a single test file with verbose output. |

### Monitoring & Debugging

| Script | Description |
|---|---|
| `./scripts/status.sh` | Shows the full system status: queue depths, Lambda configurations, EventBridge rules, and recent log activity. Run this first when something seems wrong. |
| `./scripts/logs.sh consumer 10` | View consumer Lambda logs from the last 10 minutes. Also accepts `scheduler` or `all` (default). Minutes default to 5 if not specified. |
| `./scripts/peek_queue.sh` | Inspect messages in the main queue without consuming them. Pass `dlq` to peek at the dead letter queue instead: `./scripts/peek_queue.sh dlq` |
| `./scripts/audit_db.sh` | Runs a database health check: total records, duplicates, null/future/ancient dates, and sample records. |

### Maintenance

| Script | Description |
|---|---|
| `./scripts/purge_queues.sh` | Clears all messages from both the main queue and dead letter queue. Useful when testing or after fixing a bug that caused messages to pile up. |
| `./scripts/delete_tweets.sh 123 456` | Delete tweets by ID. Pass one or more tweet IDs as arguments. Reads Twitter credentials from your `.env` file. |

### Common Workflows

**First-time setup:**
```bash
chmod +x scripts/*.sh
./scripts/build_lambdas.sh
./scripts/test_pipeline.sh
```

**After changing code:**
```bash
./scripts/build_lambdas.sh
```

**Something's broken:**
```bash
./scripts/status.sh
./scripts/logs.sh consumer 30
./scripts/peek_queue.sh dlq
```

**Starting fresh:**
```bash
./scripts/purge_queues.sh
./scripts/test_pipeline.sh
```

---

## Monitoring

The project includes a Grafana Cloud dashboard that tracks:

- **Albums Queued Today** — how many albums the scheduler found
- **Tweets Posted** — successful tweets via custom CloudWatch metrics
- **Errors Over Time** — Lambda failures
- **Lambda Duration** — execution time trends

A Grafana alert (`alert-no-tweets.json`) fires if no tweets are posted in a 24-hour period, forwarding notifications to Telegram via SNS.

---

## Daily Schedule (UTC)

| Time | Event | Description |
|---|---|---|
| 09:00 | Scheduler runs | Queries DB, queues all matching albums to SQS |
| 10:00 | Consumer runs (1/3) | Pulls 1 album, AI verifies, tweets with cover |
| 13:00 | Consumer runs (2/3) | Pulls 1 album, AI verifies, tweets with cover |
| 16:00 | Consumer runs (3/3) | Pulls 1 album, AI verifies, tweets with cover |
| Next day | Queue expires | Remaining unposted albums are automatically removed |

---

## Key Design Decisions

**Why SQS instead of direct posting?** The queue decouples scheduling from posting. This allows spacing tweets throughout the day, automatic retries on failure, and a dead letter queue for debugging. Albums that fail verification are discarded without blocking the pipeline.

**Why AI verification?** The scraped data from Pitchfork and MusicBrainz isn't always accurate — wrong release dates, misattributed albums, or obscure entries that don't match real releases. Groq's Llama 3.3 70B catches these errors before they become embarrassing public tweets, and the free tier handles the volume easily.

**Why a Lambda layer?** Dependencies like `tweepy`, `psycopg2`, and `openai` contain compiled C extensions that must match Lambda's Linux runtime. Building them into a shared layer keeps individual Lambda zips small (~23KB) and ensures binary compatibility via the `--platform manylinux2014_x86_64` pip flag.

**Why three tweets per day?** Twitter's API rate limits and duplicate content restrictions make rapid-fire posting unreliable. Three tweets spaced three hours apart avoids rate limiting, gives each tweet time to breathe on followers' timelines, and keeps the account active without being spammy.

---

## Cost

This project runs almost entirely within free tiers:

| Service | Monthly Cost |
|---|---|
| AWS Lambda | ~$0.00 (well within free tier) |
| AWS SQS | ~$0.00 (well within free tier) |
| AWS S3 | ~$0.01 (small image storage) |
| AWS CloudWatch | ~$0.00 (basic metrics) |
| Groq AI | $0.00 (free tier, ~3 calls/day) |
| Twitter/X API | ~$1.00 (pay-per-use, ~$0.01/tweet) |
| Supabase | $0.00 (free tier) |
| Grafana Cloud | $0.00 (free tier) |
| **Total** | **~$1/month** |

---

## License

MIT
