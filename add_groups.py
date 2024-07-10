import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_groups(groups):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for group in groups:
        cursor.execute(
            "INSERT INTO groups (name) VALUES ('" + group['name'] + "')"
        )

    conn.commit()
    cursor.close()
    conn.close()


groups = [
    {'name': 'Boyz Pickleball'},
    {'name': 'Test group'}
]

if __name__ == "__main__":
    add_groups(groups)
