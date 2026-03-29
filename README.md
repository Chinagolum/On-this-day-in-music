# Artist Album Release Tracker 🎶

This project scrapes album release information for artists from Pitchfork, stores the data in a PostgreSQL database, and tweets anniversary reminders on the release dates.

---

## Features 📋

- Scrapes artist and album data dynamically using Selenium and BeautifulSoup  
- Stores album info (artist, album, release date) in PostgreSQL  
- Sends automated tweets on album release anniversaries using Tweepy  
- Configurable via environment variables for secure API keys and database credentials

---

## Setup 🧙

### Prerequisites 

- Python 3.8+  
- PostgreSQL database  
- Twitter developer account with API credentials  
- ChromeDriver installed and accessible in your PATH (for Selenium)

### Installation

1. Clone the repository

```
git clone <repo-url>
cd <repo-directory>
```

2. Create and activate a virtual environment

```
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

3. Install dependencies

```
pip install -r requirements.txt
```
4. Create a .env file in the project root and add your credentials:

```
DB_URL=postgresql://user:password@host:port/dbname
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```

---

## Database Management 🗄️

The project uses `psycopg2` to manage a PostgreSQL database.

### Schema Table: `albums`
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `SERIAL` | Primary Key |
| `title` | `TEXT` | Album Name |
| `artist` | `TEXT` | Artist Name |
| `release_date`| `DATE` | Original release date used for anniversaries |

**Note:** The `DatabaseManager` class automatically runs `CREATE TABLE IF NOT EXISTS` upon initialization.

---

## Infrastructure (Terraform) 🏗️ 
If you are using Terraform to manage your PostgreSQL instance or cloud environment, use the following core commands:

| Command | Action | 
| :--- | :--- | 
| `terraform init`| Initialize the directory and download providers.|
| `terraform plan` | Preview changes to your infrastructure. |
| `terraform apply` | Deploy the infrastructure to the cloud. |
| `terraform destroy` | Tear down all managed resources. |
---

## CI/CD Deployment 🚀

This project uses **GitHub Actions** to automatically deploy code to AWS Lambda.

### Required GitHub Secrets
Navigate to `Settings > Secrets and variables > Actions` and add:

| Secret Name | Description |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | Your Terraform-generated access key |
| `AWS_SECRET_ACCESS_KEY` | Your Terraform-generated secret key |

### Packaging Details
The Lambda requires the `lib/` directory and `psycopg2-binary`. The deployment script bundles these automatically:
- **Handler:** `schedule_tweets.lambda_handler`
- **Structure:**
  - `schedule_tweets.py`
  - `lib/db_manager.py`
  - `psycopg2/` (installed via pip)


### Manual Zip Command
If you need to bundle the code manually for Terraform:
```bash
mkdir -p build
zip -j build/schedule_tweets.zip schedule_tweets.py
```
---
# Usage 📖
- Update the database connection string and Twitter API keys in .env

- Run the scraper to update the database:
```
python scraper.py
```
- Run the tweet sender (e.g., as a scheduled job) to tweet anniversaries:

```
python tweet_sender.py
```
---
# Notes 📝
- Ensure your PostgreSQL server is running and accessible

- ChromeDriver version should match your installed Chrome browser version

- Use virtual environments to manage dependencies and avoid conflicts

License
MIT License