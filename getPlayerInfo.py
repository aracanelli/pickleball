import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def getPlayerScore(player_id, group_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute(
        "select score from player_groups where player_id = %s and group_id = %s",
        (player_id, group_id)
    )

    player_score = cursor.fetchone()
    cursor.close()
    conn.close()

    return player_score
