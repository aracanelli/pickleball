import pandas as pd
from calculate_elo import Player

# Define a class for players to manage names and ELO ratings

def save_csv_elo(high_elo, low_elo):

    # Create a dictionary to hold the data for the CSV
    data = {
        'Game 1': {},
        'Game 2': {},
        'Game 3': {},
        'Game 4': {},
        'Game 5': {}
    }

    # Define games
    games = [
        (high_elo[0], high_elo[1], high_elo[2], high_elo[3]),
        (high_elo[4], high_elo[5], high_elo[6], high_elo[7]),
        (low_elo[0], low_elo[1], low_elo[2], low_elo[3]),
        (low_elo[4], low_elo[5], low_elo[6], low_elo[7])
    ]

    # Populate the data dictionary
    for i in range(5):
        for j in range(4):
            team1_player1 = games[j][0]
            team1_player2 = games[j][1]
            team2_player1 = games[j][2]
            team2_player2 = games[j][3]

            team1 = f"{team1_player1.name} and {team1_player2.name} ({(team1_player1.elo + team1_player2.elo) / 2})"
            team2 = f"{team2_player1.name} and {team2_player2.name} ({(team2_player1.elo + team2_player2.elo) / 2})"

            data[f'Game {i+1}'][f'Team {j*2+1}'] = team1
            data[f'Game {i+1}'][f'Team {j*2+2}'] = team2
            data[f'Game {i+1}'][f'Team {j*2+1} Score'] = ""
            data[f'Game {i+1}'][f'Team {j*2+2} Score'] = ""

    # Convert the data into a DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv('pickleball_games.csv', index=False)

    print("CSV file has been generated successfully.")

    # Print the games as specified
    for i in range(5):
        print(f"Set {i+1}")
        for j in range(4):
            print(f"Game {j+1}: {data[f'Game {i+1}'][f'Team {j*2+1}']} vs {data[f'Game {i+1}'][f'Team {j*2+2}']}")
