import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def create_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id SERIAL PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        email VARCHAR(100) DEFAULT NULL,
        average_score INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        group_id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        UNIQUE(name)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_groups (
        player_groups_id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(player_id),
        group_id INTEGER REFERENCES groups(group_id),
        ranking INTEGER DEFAULT 1,
        score INTEGER DEFAULT 0,
        UNIQUE(player_id,group_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams (
        team_id SERIAL PRIMARY KEY,
        group_id INTEGER REFERENCES groups(group_id),
        player1_id INTEGER REFERENCES players(player_id),
        player2_id INTEGER REFERENCES players(player_id),
        UNIQUE(group_id,player1_id, player2_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id SERIAL PRIMARY KEY,
        group_id INTEGER REFERENCES groups(group_id),
        team1_id INTEGER REFERENCES teams(team_id),
        team2_id INTEGER REFERENCES teams(team_id),
        UNIQUE(group_id,team1_id, team2_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        match_id SERIAL PRIMARY KEY,
        team1_id INTEGER REFERENCES teams(team_id),
        team2_id INTEGER REFERENCES teams(team_id),
        match_date DATE DEFAULT CURRENT_DATE,
        score1 INTEGER DEFAULT 0,
        score2 INTEGER DEFAULT 0
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    create_tables()
