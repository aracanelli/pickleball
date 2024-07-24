import psycopg2
from dotenv import load_dotenv
import os

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
    return group_id[0]

def fetch_players(group_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.player_id, p.nick_name, pg.sub 
        FROM player_groups pg, players p 
        WHERE p.player_id = pg.player_id and group_id = 
    """ + str(group_id))
    games = cursor.fetchall()

    cursor.close()
    conn.close()

    return games

def fetch_history(group_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT player1_id, player2_id, player3_id, player4_id, score1, score2
        FROM history
    """)

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return history