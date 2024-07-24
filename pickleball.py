import database_fetch
from calculate_elo import Games, Player2
from itertools import combinations
import random
import csv

def print_game_schedule(game_title, game_players):
    def print_court(court_number, player1, player2, player3, player4):
        team1_avg_elo = round((player1.elo + player2.elo) / 2, 1)
        team2_avg_elo = round((player3.elo + player4.elo) / 2, 1)
        print(
            f"Court {court_number:02}: {player1.name} and {player2.name} ({team1_avg_elo}) vs {player3.name} and {player4.name} ({team2_avg_elo})")

    print(game_title)
    for i, court_number in enumerate(range(9, 13)):
        players = game_players[i * 4:(i + 1) * 4]
        print_court(court_number, *players)
    print()


def play_games():
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


def print_ranks(printed_players, full_time=True):
    print("Full-time players sorted by ELO:")
    for rank, player in enumerate(printed_players, start=1):
        if full_time:
            if player.sub == False:
                print(f"Rank: {rank}, Name: {player.name}, ELO: {round(player.elo,1)}, Wins: {player.wins}")
        else:
            print(f"Rank: {rank}, Name: {player.name}, ELO: {round(player.elo, 1)}, Wins: {player.wins}")
    print(f"")


def pair_exists(match_pair, played_matches):
    for pair in match_pair:
        for match in played_matches:
            if (pair[0].id, pair[1].id) in match or (pair[1].id, pair[0].id) in match:
                return True

    return False


def opponent_exists(match_pair, played_matches):

    player1 = played_matches[0][0].id
    player2 = played_matches[0][1].id
    player3 = played_matches[1][0].id
    player4 = played_matches[1][1].id

    team1_ids = (match_pair[0][0].id, match_pair[0][1].id)
    team2_ids = (match_pair[1][0].id, match_pair[1][1].id)

    condition1 = player1 in team1_ids and (player3 in team2_ids or player4 in team2_ids)
    condition2 = player1 in team2_ids and (player3 in team1_ids or player4 in team1_ids)
    condition3 = player2 in team1_ids and (player3 in team2_ids or player4 in team2_ids)
    condition4 = player2 in team2_ids and (player3 in team1_ids or player4 in team1_ids)
    condition5 = player3 in team1_ids and (player1 in team2_ids or player2 in team2_ids)
    condition6 = player3 in team2_ids and (player1 in team1_ids or player2 in team1_ids)
    condition7 = player4 in team1_ids and (player1 in team2_ids or player2 in team2_ids)
    condition8 = player4 in team2_ids and (player1 in team1_ids or player2 in team1_ids)

    all_conditions = condition1 or condition2 or condition3 or condition4 or condition5 or condition6 or condition7 or condition8

    if all_conditions:
        return True

    return False


# Function to check if a match should be removed
def should_remove(match, played_matches, remove_opponents):
    if remove_opponents:
        return opponent_exists(match, played_matches)
    else:
        return pair_exists(match, played_matches)


def remove_matchups(all_matches, matches_to_remove, remove_opponents=False):
    return [match for match in all_matches if not should_remove(match, matches_to_remove, remove_opponents)]


def get_previous_games(games_to_load):
    player_dict = {player.id: player for player in sorted_players}
    temp_player_list = []

    for game in games_to_load:
        temp_player_list.extend(game[:4])

    new_player_list = [player_dict[player_id] for player_id in temp_player_list]
    previous_games_to_load = []
    for i in range(0, len(new_player_list), 4):
        team1 = (new_player_list[i].id, new_player_list[i+1].id)
        team2 = (new_player_list[i+2].id, new_player_list[i+3].id)

        previous_games_to_load = previous_games_to_load + [[team1, team2]]
    return previous_games_to_load


def validate_elo_split_games(game_matchups):
    max_id = 0
    for game in game_matchups:
        team1 = game[0]
        team2 = game[1]
        for player in team1 + team2:
            if player > max_id:
                max_id = player

    max_id += 1  # To accommodate 0-based indexing
    elo_split_opponents = [[0] * max_id for _ in range(max_id)]
    elo_split_teammates = [[0] * max_id for _ in range(max_id)]

    for game in game_matchups:
        team1 = game[0]
        team2 = game[1]

        elo_split_teammates[team1[1]][team1[0]] += 1
        elo_split_teammates[team1[0]][team1[1]] += 1
        elo_split_teammates[team2[0]][team2[1]] += 1
        elo_split_teammates[team2[1]][team2[0]] += 1

        elo_split_opponents[team1[0]][team2[0]] += 1
        elo_split_opponents[team1[0]][team2[1]] += 1
        elo_split_opponents[team1[1]][team2[0]] += 1
        elo_split_opponents[team1[1]][team2[1]] += 1

        elo_split_opponents[team2[0]][team1[0]] += 1
        elo_split_opponents[team2[0]][team1[1]] += 1
        elo_split_opponents[team2[1]][team1[0]] += 1
        elo_split_opponents[team2[1]][team1[1]] += 1

    for teammate in elo_split_teammates:
        for i in teammate:
            if i > 1:
                return True, []

    for opponent in elo_split_opponents:
        for i in opponent:
            if i > 1:
                return True, []

    return False, elo_split_opponents


def validate_elo_based_games(game_matchups, prev_opponents, old_filtered_matchups):

    elo_based_opponents = prev_opponents
    new_filtered_matchups = old_filtered_matchups

    for game in game_matchups:
        team1 = game[0]
        team2 = game[1]

        elo_based_opponents[team1[0].id][team2[0].id] += 1
        elo_based_opponents[team1[0].id][team2[1].id] += 1
        elo_based_opponents[team1[1].id][team2[0].id] += 1
        elo_based_opponents[team1[1].id][team2[1].id] += 1

        elo_based_opponents[team2[0].id][team1[0].id] += 1
        elo_based_opponents[team2[0].id][team1[1].id] += 1
        elo_based_opponents[team2[1].id][team1[0].id] += 1
        elo_based_opponents[team2[1].id][team1[1].id] += 1

        for opponent in elo_based_opponents:
            for idx in range(len(opponent)):
                if opponent[idx] > 1:
                    opponent[idx] = 0
                    new_filtered_matchups = remove_matchups(new_filtered_matchups, game, True)

    return new_filtered_matchups, elo_based_opponents

def generate_elo_split_games(num_of_games):
    game_matchups = []
    player_order = []
    elo_split_opponents = []
    games_not_found = True
    while games_not_found:
        game_matchups = []
        player_order = []
        for _ in range(1, num_of_games + 1):
            elo_line = int(len(sorted_playing_players) / 2)
            high_elo = sorted_playing_players[:elo_line]
            low_elo = sorted_playing_players[elo_line:]
            random.shuffle(high_elo)
            random.shuffle(low_elo)

            game1 = [[(high_elo[0].id, high_elo[1].id), (high_elo[2].id, high_elo[3].id)]]
            game2 = [[(high_elo[4].id, high_elo[5].id), (high_elo[6].id, high_elo[7].id)]]
            game3 = [[(low_elo[0].id, low_elo[1].id), (low_elo[2].id, low_elo[3].id)]]
            game4 = [[(low_elo[4].id, low_elo[5].id), (low_elo[6].id, low_elo[7].id)]]

            game_matchups = game_matchups + game1 + game2 + game3 + game4

            player_order.extend(
                [high_elo[0], high_elo[1], high_elo[2], high_elo[3], high_elo[4], high_elo[5], high_elo[6], high_elo[7],
                 low_elo[0], low_elo[1], low_elo[2], low_elo[3], low_elo[4], low_elo[5], low_elo[6], low_elo[7]])

        games_not_found, elo_split_opponents = validate_elo_split_games(game_matchups)
    return game_matchups, player_order, elo_split_opponents


def find_unique_matches(random_matches):
    while True:
        random.shuffle(random_matches)
        selected_matches = []
        selected_players = []
        used_players = set()

        for match in random_matches:
            players_in_match = set(match[0] + match[1])
            if not players_in_match & used_players:
                selected_matches.append(match)
                selected_players.extend([match[0][0], match[0][1], match[1][0], match[1][1]])
                used_players.update(players_in_match)
                if len(selected_matches) == 4:
                    return selected_matches, selected_players


def valid_generated_matches(generated_matches,  elo_dif):
    valid_matches = []
    for match in generated_matches:
        team_elo1 = (match[0][0].elo + match[0][1].elo) / 2
        team_elo2 = (match[1][0].elo + match[1][1].elo) / 2

        if abs(team_elo1 - team_elo2) / max(team_elo1, team_elo2) <= elo_dif:
            valid_matches.append(match)

    return valid_matches

def replace_name(players_list, old_name, new_name):
    for i, name in enumerate(players_list):
        if name == old_name:
            players_list[i] = new_name
            break


def create_game_csv(players_list, num_games, num_courts, filename="games.csv"):
    # Determine the number of games
    num_players_on_court = 4
    num_players = int(len(players_list) / num_courts / num_games * num_players_on_court)
    # Open the CSV file for writing
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the headers for each game
        headers = []
        for game_num in range(1, num_games + 1):
            headers.extend([f"Game {game_num}", ""])
        writer.writerow(headers)

        for court_num in range(num_courts):
            row_team_names = []
            row_team_1 = []
            row_team_2 = []

            for game_num in range(num_games):
                row_team_names.extend([f"Team {(court_num*2) + 1}", f"Team {(court_num*2) + 2}"])

                replace_name(players_list, "Falcone", "Mike")
                replace_name(players_list, "Baller", "Ballerini")
                replace_name(players_list, "Steve", "Steven")

                idx = (court_num * num_courts) + (game_num * num_players)

                row_1 = [players_list[0 + idx], players_list[2 + idx]]
                row_2 = [players_list[1 + idx], players_list[3 + idx]]

                row_team_1.extend(row_1)
                row_team_2.extend(row_2)

            writer.writerow(row_team_names)
            writer.writerow(row_team_1)
            writer.writerow(row_team_2)
            writer.writerow(["", ""])  # Empty row for spacing


if __name__ == "__main__":
    group_id = database_fetch.get_group_id("Boyz Pickleball")
    player_ids = database_fetch.fetch_players(group_id)
    games = database_fetch.fetch_history(group_id)

    players = {player_id: Player2(player_id, player_name, sub) for player_id, player_name, sub in player_ids}
    name_to_player = {player.name: player for player in players.values()}

    play_games()

    sorted_players = sorted(players.values(), key=lambda player: player.elo, reverse=True)
    sorted_ft_players = sorted([player for player in players.values() if not player.sub], key=lambda x: x.elo, reverse=True)

    print_ranks(sorted_ft_players)
    print_ranks(sorted_players, False)

    player_list = [
        "Anthony",
        "Matt",
        "James",
        "Steve",
        "Felix",
        "Falcone",
        "Fred",
        "Mass",
        "Samantha",
        "Cha-Nel",
        "Erica",
        "Baller",
        "Sam",
        "Taurasi",
        "Sandra",
        "James C"
    ]

    sorted_playing_players = sorted([name_to_player[name] for name in player_list], key=lambda x: x.elo, reverse=True)
    pairs = list(combinations(sorted_playing_players, 2))
    matches = [(p1, p2) for p1 in pairs for p2 in pairs if not set(p1) & set(p2)]
    previous_games = get_previous_games(games[-20:])
    filtered_matchup = remove_matchups(matches, previous_games)

    num_elo_split_games = 2
    num_elo_based_games = 3
    elo_dif = 0.1

    elo_split_games, elo_split_players, opponents = generate_elo_split_games(num_elo_split_games)

    game_players = [player.name for player in elo_split_players]

    for i in range(1, num_elo_split_games + 1):
        start_index = (i - 1) * 16
        end_index = i * 16
        current_game_players = elo_split_players[start_index:end_index]
        print_game_schedule(f"Game {i}", current_game_players)

    new_filtered_matchup = remove_matchups(filtered_matchup, elo_split_games)
    new_filtered_matchup = valid_generated_matches(new_filtered_matchup, elo_dif)

    elo_based_players = []

    for _ in range(1, num_elo_based_games + 1):
        random.shuffle(new_filtered_matchup)
        result_matches, result_players = find_unique_matches(new_filtered_matchup)
        game_players = game_players + [player.name for player in result_players]
        result_ids = [[(team[0].id, team[1].id) for team in match] for match in result_matches]
        new_filtered_matchup = remove_matchups(new_filtered_matchup, result_ids)
        for matchup in result_matches:
            for player in matchup:
                elo_based_players.extend([player[0], player[1]])
        new_filtered_matchup, opponents = validate_elo_based_games(result_matches, opponents, new_filtered_matchup)

    for i in range(1, num_elo_based_games + 1):
        start_index = (i - 1) * 16
        end_index = i * 16
        current_game_players = elo_based_players[start_index:end_index]
        print_game_schedule(f"Game {i + num_elo_split_games}", current_game_players)

    create_game_csv(game_players, 5, 4)

