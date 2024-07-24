from itertools import combinations
import pickle
import random
import os
from dotenv import load_dotenv
from copy import deepcopy
from calculate_elo import Player, Games

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


class BreakOut(Exception):
    pass


class player_history:
    def __init__(self, player):
        self.player = player
        self.opponents = {}
        self.teammates = set()

    def add_opponents(self, opponent1, opponent2):
        self._add_opponent(opponent1)
        self._add_opponent(opponent2)

    def _add_opponent(self, opponent):
        if opponent in self.opponents:
            self.opponents[opponent] += 1
        else:
            self.opponents[opponent] = 1

    def opponents_more_than_once(self):
        return len({opponent: count for opponent, count in self.opponents.items() if count > 1})

    def unique_opponents_count(self):
        return len(self.opponents)

    def get_opponents(self):
        return self.opponents

    def get_opponent_count(self, opponent):
        return self.opponents.get(opponent, 0)

    def __str__(self):
        opponents_str = ', '.join([f"{op}: {count}" for op, count in self.opponents.items()])
        return (f"Player: {self.player}\n"
                f"Opponents: {opponents_str}")


class match_history:
    def __init__(self, sorted_players):
        self.sorted_players = sorted_players
        self.players = {sorted_player.id: player_history(sorted_player) for sorted_player in sorted_players}
        self.previous_teammate_count = 0
        self.restart = False
        self.games_scheduled = 0
        self.previous_games = []

    def print_game_schedule(self, game_title, game_players):
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

    def calculate_average(self, test_players, game_players):
        averages = []
        matches = []

        # Calculate average ELO for each team
        for i in range(0, len(game_players), 2):
            average = (test_players[game_players[i].id].player.elo +
                       test_players[game_players[i + 1].id].player.elo)
            averages.append(average)

        # Calculate match differences
        for i in range(0, len(averages), 2):
            match = abs(averages[i] - averages[i + 1]) / max(averages[i], averages[i + 1])
            matches.append(match)

        return tuple(matches)

    def update_teammates(self, test_players, high_elo, low_elo):
        def add_teammates_for_group(elo_group):
            for i in range(0, len(elo_group), 2):
                test_players[elo_group[i].id].teammates.update([elo_group[i + 1].name])
                test_players[elo_group[i + 1].id].teammates.update([elo_group[i].name])

        add_teammates_for_group(high_elo)
        add_teammates_for_group(low_elo)

        return test_players

    def update_teammates_single(self, test_players, elo):
        num_players = len(elo)
        for i in range(0, num_players, 2):
            if elo[i].id in test_players:
                test_players[elo[i].id].teammates.update([elo[i + 1].name])
            if elo[i + 1].id in test_players:
                test_players[elo[i + 1].id].teammates.update([elo[i].name])

        return test_players

    def update_opponents(self, players, high_elo, low_elo):
        def add_opponents_for_group(elo_group):
            for i in range(0, len(elo_group), 4):
                players[elo_group[i].id].add_opponents(elo_group[i + 2].name, elo_group[i + 3].name)
                players[elo_group[i + 1].id].add_opponents(elo_group[i + 2].name, elo_group[i + 3].name)
                players[elo_group[i + 2].id].add_opponents(elo_group[i].name, elo_group[i + 1].name)
                players[elo_group[i + 3].id].add_opponents(elo_group[i].name, elo_group[i + 1].name)

        add_opponents_for_group(high_elo)
        add_opponents_for_group(low_elo)

        return players

    def update_opponents_single(self, players, elo):
        for i in range(0, len(elo), 4):
            players[elo[i].id].add_opponents(elo[i + 2].name, elo[i + 3].name)
            players[elo[i + 1].id].add_opponents(elo[i + 2].name, elo[i + 3].name)
            players[elo[i + 2].id].add_opponents(elo[i].name, elo[i + 1].name)
            players[elo[i + 3].id].add_opponents(elo[i].name, elo[i + 1].name)

        return players

    def print_opponent_count(self):
        for player in self.players.values():
            print(f"{player.player.name}: Opponents: {player.unique_opponents_count()}")

    def valid_generated_matches(self, matches, test_players, elo_dif):
        valid_matches = []
        for match in matches:
            team_elo1 = (test_players[match[0][0]].player.elo + test_players[match[0][1]].player.elo) / 2
            team_elo2 = (test_players[match[1][0]].player.elo + test_players[match[1][1]].player.elo) / 2

            if abs(team_elo1 - team_elo2) / max(team_elo1, team_elo2) <= elo_dif:
                valid_matches.append(match)

        return valid_matches
    def validate_matches(self, matches, teammates_count, test_players):
        expected_teammates_count = len(matches)
        if teammates_count == expected_teammates_count + self.previous_teammate_count:
            return False
        else:
            return True

    def pair_exists(self, pairs, played_matches):
        for match in played_matches:
            player1 = match [0][0]
            player2 = match [0][1]
            player3 = match [1][0]
            player4 = match [1][1]

            if (player1 in pairs[0] or player2 in pairs[0]) and (player3 in pairs[1] or player4 in pairs[1]):
                return True
            if (player1 in pairs[1] or player2 in pairs[1]) and (player3 in pairs[0] or player4 in pairs[0]):
                return True

        for pair in pairs:
            for match in played_matches:
                if pair in match or (pair[1], pair[0]) in match:
                    return True
            return False

    def pair_exists2(self, pairs, played_matches):
        for match in played_matches:
            match_players = {match[0][0], match[0][1], match[1][0], match[1][1]}

            # Check if the pairs intersect with the match players
            if (set(pairs[0]) & match_players and set(pairs[1]) & match_players) or (
                    set(pairs[1]) & match_players and set(pairs[0]) & match_players):
                return True

        return False

    # Function to check if a match should be removed
    def should_remove(self, match, played_matches):
        return self.pair_exists2(match, played_matches)
    def generate_games(self, elo_split, elo_based, elo_dif, elo_dif_increase=True):
        matches = []
        game_not_found = True
        sorted_players = self.sorted_players[:]
        test_players = deepcopy(self.players)

        pairs = list(combinations(test_players, 2))
        matches = [(p1, p2) for p1 in pairs for p2 in pairs if not set(p1) & set(p2)]
        print(f"Generated {len(pairs)} pairs and {len(matches)} matches")

        valid_matches = self.valid_generated_matches(matches, test_players, elo_dif)
        print(f"Valid matches: {len(valid_matches)}")

        filtered_matches = [match for match in valid_matches if not self.should_remove(match, self.previous_games)]
        print("Generating Games 1 and 2")
        while game_not_found:
            matches = []
            test_players = deepcopy(self.players)
            teammates_count = 0

            filtered_matches = [match for match in valid_matches if not self.should_remove(match, self.previous_games)]

            for _ in range(1, elo_split + 1):
                elo_line = int(len(self.sorted_players) / 2)
                high_elo = self.sorted_players[:elo_line]
                low_elo = self.sorted_players[elo_line:]
                random.shuffle(high_elo)
                random.shuffle(low_elo)

                test_players = self.update_teammates(test_players, high_elo, low_elo)
                test_players = self.update_opponents(test_players, high_elo, low_elo)

                team1 = (high_elo[0].id, high_elo[1].id)
                team2 = (high_elo[2].id, high_elo[3].id)
                team3 = (high_elo[4].id, high_elo[5].id)
                team4 = (high_elo[6].id, high_elo[7].id)
                team5 = (low_elo[0].id, low_elo[1].id)
                team6 = (low_elo[2].id, low_elo[3].id)
                team7 = (low_elo[4].id, low_elo[5].id)
                team8 = (low_elo[6].id, low_elo[7].id)

                matches_to_remove = [[team1,team2],[team3,team4],[team5,team6],[team7,team8]]

                matches = matches + high_elo + low_elo
                filtered_matches = [match for match in filtered_matches if not self.should_remove(match, matches_to_remove)]


            for player in test_players.values():
                teammates_count += len(player.teammates)

            game_not_found = self.validate_matches(matches, teammates_count, 16)
        print(f"Filtered matches: {len(filtered_matches)}")
        print("Generating Games 3, 4 and 5")
        for _ in range(1, elo_based + 1):
            result_matches = self.find_unique_matches(filtered_matches, test_players)
            filtered_matches = [match for match in filtered_matches if not self.should_remove(match, result_matches)]
            print(result_matches)

        print(f"Filtered matches: {len(filtered_matches)}")

        for i in range(1, elo_split + 1):
            start_index = (i - 1) * 16
            end_index = i * 16
            current_game_players = matches[start_index:end_index]
            self.print_game_schedule(f"Game {i}", current_game_players)

    def load_previous_week(self, games, players):
        player_dict = {player.id: player for player in players}
        player_list = []

        for game in games:
            player_list.extend(game[:4])

        new_player_list = [player_dict[player_id] for player_id in player_list]
        self.update_previous_games(new_player_list)
        for i in range(0, len(new_player_list), 16):
            process_list = new_player_list[i:i + 16]
            self.players = self.update_teammates_single(self.players, process_list)

        for player in self.players.values():
            self.previous_teammate_count += len(player.teammates)

    def update_previous_games(self, players_list):
        for i in range(0, len(players_list), 4):
            team1 = (players_list[i].id, players_list[i+1].id)
            team2 = (players_list[i+2].id, players_list[i+3].id)

            self.previous_games = self.previous_games + [[team1, team2]]

    def find_unique_matches(self, matches, num_players):
        while True:
            random.shuffle(matches)
            selected_matches = []
            used_players = set()

            for match in matches:
                players_in_match = set(match[0] + match[1])
                if not players_in_match & used_players:
                    selected_matches.append(match)
                    used_players.update(players_in_match)
                    if len(selected_matches) == 4:
                        return selected_matches

