import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def add_players(players):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for player in players:
        cursor.execute(
            "INSERT INTO players (first_name, last_name) VALUES (%s, %s)",
            (player['first_name'], player['last_name'])
        )

    conn.commit()
    cursor.close()
    conn.close()


players = [
    {'first_name': 'Anthony', 'last_name': 'Racanelli'},
    {'first_name': 'Cha-Nel', 'last_name': 'Rocheleau'},
    {'first_name': 'Daniel', 'last_name': 'Ballerini'},
    {'first_name': 'Erica', 'last_name': 'Petreccia'},
    {'first_name': 'Giancarlo', 'last_name': 'Szymborski'},
    {'first_name': 'James', 'last_name': 'Akkaoui'},
    {'first_name': 'Jenna', 'last_name': 'Moledina'},
    {'first_name': 'Matthew', 'last_name': 'Racanelli'},
    {'first_name': 'Michael', 'last_name': 'Scarfo'},
    {'first_name': 'Michael', 'last_name': 'Falcone'},
    {'first_name': 'Samuel', 'last_name': 'McAuliffe'},
    {'first_name': 'Sandra', 'last_name': 'Marino'},
    {'first_name': 'Sarah', 'last_name': 'Petreccia'},
    {'first_name': 'Steven', 'last_name': 'Abruzzese'},
    {'first_name': 'Victoria', 'last_name': 'Pacitto'},
    {'first_name': 'Daniele', 'last_name': 'Taurasi'},
]

if __name__ == "__main__":
    add_players(players)
