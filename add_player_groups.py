import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_player_ids():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("select player_id from players")

    player_ids = cursor.fetchall()

    cursor.close()
    conn.close()
    return player_ids


def get_group_id(name):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("select group_id from groups where name = '" + name + "'")

    group_id = cursor.fetchone()

    cursor.close()
    conn.close()
    return group_id


def add_player_groups(players, group):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for player in players:
        cursor.execute(
            "INSERT INTO player_groups (player_id, group_id) VALUES (%s, %s)",
            (player, group)
        )

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    players = get_player_ids()
    group = get_group_id("Boyz Pickleball")
    add_player_groups(players, group)
