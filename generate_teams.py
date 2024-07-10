import itertools
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_group_id(name):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("select group_id from groups where name = '" + name + "'")

    group_id = cursor.fetchone()

    cursor.close()
    conn.close()
    return group_id

def generate_teams(group_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("SELECT player_id FROM player_groups where group_id = " + str(group_id[0]))
    players = cursor.fetchall()

    teams = list(itertools.combinations(players, 2))

    for team in teams:
        cursor.execute(
            "INSERT INTO teams (group_id, player1_id, player2_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (group_id, team[0][0], team[1][0])
        )

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    group_id = get_group_id("Boyz Pickleball")
    generate_teams(group_id)
