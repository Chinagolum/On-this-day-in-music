import psycopg2
import logging
from lib.config import DB_URL

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        logger.info(f"Connecting to database... {DB_URL}")  # FIXED: Added f-string
        self.conn = psycopg2.connect(DB_URL)
        self.c = self.conn.cursor()
        self.create_table()
        logger.info("Database connected successfully")


    def create_table(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                genre TEXT,
                release_date DATE,
                reviewer TEXT,
                review_date DATE,
                image_url TEXT,
                UNIQUE(title, artist)
            );
        ''')
        self.conn.commit()

    def insert_entry(self, title, artist, genre=None, release_date=None, reviewer=None, review_date=None, image_url=None):
        """
        Inserts a new album entry into the albums table.
        """
        if not title or not artist:
            raise ValueError("title and artist are required.")

        self.c.execute(
            """
            INSERT INTO albums (title, artist, genre, release_date, reviewer, review_date, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (title, artist) DO NOTHING
            """,
            (title, artist, genre, release_date, reviewer, review_date, image_url)
        )
        self.conn.commit()

        if self.c.rowcount == 0:
            logger.info(f"Skipped duplicate: {title} by {artist}")
        else:
            logger.info(f"Inserted: {title} by {artist}")


    def fetch_by_release_date(self, date):
        """
        Fetch all albums where the release_date matches the month and day of the given date.
        date: string in 'YYYY-MM-DD' format
        """
        if not date or len(date) != 10 or date[4] != '-' or date[7] != '-':  # ← UPDATE THIS
            raise ValueError("date must be in 'YYYY-MM-DD' format")

        month_day = date[5:10]
        self.c.execute(
            "SELECT * FROM albums WHERE TO_CHAR(release_date, 'MM-DD') = %s",
            (month_day,)
        )
        return self.c.fetchall()


    def fetch_by_review_date(self, date):
        """
        Fetch all albums where the review_date matches the month and day of the given date.
        date: string in 'YYYY-MM-DD' format
        """
        if not date or len(date) != 10:
            raise ValueError("date must be in 'YYYY-MM-DD' format")

        month_day = date[5:10]
        self.c.execute(
            "SELECT * FROM albums WHERE TO_CHAR(review_date, 'MM-DD') = %s",
            (month_day,)
        )
        return self.c.fetchall()


    def fetch_all(self):
        """
        Fetch all albums from the albums table.
        """
        self.c.execute("SELECT * FROM albums ORDER BY release_date")
        return self.c.fetchall()


    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()