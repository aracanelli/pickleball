import itertools
import psycopg2
import os
from generate_matches import match_history, player_history
from calculate_elo import Games, Player
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def print_all(sorted_players):
    print("All players sorted by ELO:")
    for rank, player in enumerate(sorted_players, start=1):
        #if player.sub == False:
        print(f"Rank: {rank}, Name: {player.name}, ELO: {round(player.elo,1)}, Wins: {player.wins}")
    print(f"")
def print_full_time(sorted_players):
    print("Full-time players sorted by ELO:")
    for rank, player in enumerate(sorted_players, start=1):
        if player.sub == False:
            print(f"Rank: {rank}, Name: {player.name}, ELO: {round(player.elo,1)}, Wins: {player.wins}")
    print(f"")
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

def play_games(games):
    for game in games:
        match = Games()
        player1 = players[game[0]]
        player2 = players[game[1]]
        player3 = players[game[2]]
        player4 = players[game[3]]
        elo1 = player1.elo
        elo2 = player2.elo
        elo3 = player3.elo
        elo4 = player4.elo

        match.set_team(player1, player2, player3, player4)
        match.set_winner(game[4], game[5])
        match.update_elo()
        print(f"Game: {player1.name}, {player2.name} vs {player3.name}, {player4.name}")
        print(f"Score: {game[4]} - {game[5]}")
        print(f"Team 1 elo: {round(match.team1_elo, 1)}, Team 2 elo: {round(match.team2_elo, 1)}")
        print(f"Old elo: {round(elo1, 1)}, New elo: {player1.name} - {round(player1.elo, 1)}, Elo diff: {round(player1.elo - elo1, 1)}, E1 = {round(match.E1, 2)}")
        print(f"Old elo: {round(elo2, 1)}, New elo: {player2.name} - {round(player2.elo, 1)}, Elo diff: {round(player2.elo - elo2, 1)}, E2 = {round(match.E2, 2)}")
        print(f"Old elo: {round(elo3, 1)}, New elo: {player3.name} - {round(player3.elo, 1)}, Elo diff: {round(player3.elo - elo3, 1)}, E3 = {round(match.E3, 2)}")
        print(f"Old elo: {round(elo4, 1)}, New elo: {player4.name} - {round(player4.elo, 1)}, Elo diff: {round(player4.elo - elo4, 1)}, E4 = {round(match.E4, 2)}")
        print(f"")

if __name__ == "__main__":
    group_id = get_group_id("Boyz Pickleball")
    player_ids = fetch_players(group_id)
    games = fetch_history(group_id)

    players = {player_id: Player(player_id, player_name, sub) for player_id, player_name, sub in player_ids}
    name_to_player = {player.name: player for player in players.values()}

    play_games(games)

    sorted_players = sorted(players.values(), key=lambda player: player.elo, reverse=True)
    sorted_fulltime_players = sorted([player for player in players.values() if not player.sub], key=lambda x: x.elo, reverse=True)

    print_all(sorted_players)
    #print_full_time(sorted_fulltime_players)

    player_list = [
        "Anthony",
        "Felix",
        "James",
        "Matt",
        "Jenna",
        "Falcone",
        "Szymbo",
        "Fred",
        "Scarfo",
        "Cha-Nel",
        "Erica",
        "Silvio",
        "Sam",
        "Taurasi",
        "Sandra",
        "Sarah"
    ]

    sorted_playing_players = sorted([name_to_player[name] for name in player_list], key=lambda x: x.elo, reverse=True)
    history = match_history(sorted_playing_players)
    history.load_previous_week(games[-20:], sorted_players)
    #history.generate_games()