import psycopg2
from config import POSTGRES_DSN

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(POSTGRES_DSN)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS artistInfo (
                aID SERIAL PRIMARY KEY,
                artist TEXT NOT NULL,
                album TEXT NOT NULL,
                releaseDate DATE NOT NULL
            );
        ''')
        self.conn.commit()

    def insert_entry(self, artist, album, release_date):
        self.c.execute(
            "INSERT INTO artistInfo (artist, album, releaseDate) VALUES (%s, %s, %s)",
            (artist, album, release_date)
        )
        self.conn.commit()

    def fetch_by_date(self, date):
        self.c.execute(
            "SELECT * FROM artistInfo WHERE TO_CHAR(releaseDate, 'MM-DD') = %s",
            [date[5:10]]
        )
        return self.c.fetchall()

    def fetch_all(self):
        self.c.execute("SELECT * FROM artistInfo")
        return self.c.fetchall()

    def close(self):
        self.conn.close()
