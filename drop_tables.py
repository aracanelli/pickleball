import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def drop_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS history CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS matches CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS teams CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS player_groups CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS groups CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS players CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS rankings CASCADE;")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    drop_tables()
