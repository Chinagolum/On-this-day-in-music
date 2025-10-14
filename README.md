# Artist Album Release Tracker

This project scrapes album release information for artists from Pitchfork, stores the data in a PostgreSQL database, and tweets anniversary reminders on the release dates.

---

## Features

- Scrapes artist and album data dynamically using Selenium and BeautifulSoup  
- Stores album info (artist, album, release date) in PostgreSQL  
- Sends automated tweets on album release anniversaries using Tweepy  
- Configurable via environment variables for secure API keys and database credentials

---

## Setup

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
DATABASE_URL=postgresql://user:password@host:port/dbname
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_CONSUMER_SECRET=your_consumer_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
```
---
# Usage
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
# Notes
- Ensure your PostgreSQL server is running and accessible

- ChromeDriver version should match your installed Chrome browser version

- Use virtual environments to manage dependencies and avoid conflicts

License
MIT License