import csv
import random
import os
from dotenv import load_dotenv
from copy import deepcopy

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
        self.game_players1 = []
        self.game_players2 = []
        self.game_players3 = []
        self.game_players4 = []
        self.game_players5 = []

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

    def generate_games(self):
        self.restart = False

        #self.generate_elo_split_games(elo_split)
        #self.games_scheduled = elo_split

        #self.generate_elo_based_games(elo_based, elo_diff)
        #self.games_scheduled = elo_based + elo_split

        #self.generate_all_games2(elo_split, elo_based, elo_diff)
        self.Game1()
        self.Game2()
        self.Game3()
        self.Game4()
        self.Game5()

        self.create_game_csv([self.game_players1, self.game_players2, self.game_players3, self.game_players4, self.game_players5])

    def load_previous_week(self, games, players):
        player_dict = {player.id: player for player in players}
        player_list = []
        for game in games:
            player_list.extend(game[:4])

        new_player_list = [player_dict[player_id] for player_id in player_list]

        self.players = self.update_teammates_single(self.players, new_player_list)

        for player in self.players.values():
            self.previous_teammate_count += len(player.teammates)

    def validate_elo_split_games(self, num, teammates_count, test_players):
        expected_teammates_count = num * len(self.sorted_players)
        if teammates_count == expected_teammates_count + self.previous_teammate_count:
            for player in test_players.values():
                for opponents, count in player.get_opponents().items():
                    if count > 1 or player.opponents_more_than_once() > 1:
                        return True
                    else:
                        continue
            return False
        else:
            return True

    def validate_games(self, num, teammates_count, test_players, tolerance=None):
        expected_teammates_count = num * len(self.sorted_players)
        if teammates_count != expected_teammates_count + self.previous_teammate_count:
            return True

        for player in test_players.values():
            for opponents, count in player.get_opponents().items():
                if count > 2 or player.opponents_more_than_once() > 1:
                    return True

        if tolerance is not None:
            for i in range(1, num + 1):
                start_index = (i - 1) * 16
                end_index = i * 16
                current_sorted_players = self.sorted_players[start_index:end_index]
                current_tolerance = tolerance + ((i-1) * 0.05)

                game_matches = self.calculate_average(test_players, current_sorted_players)
                if any(match > current_tolerance for match in game_matches):
                    return True

        return False

    def generate_all_games2(self, num_split, num_based, elo_dif):
        def generate_single_type(num, elo_split):
            game_players = []
            game_not_found = True
            test_players = deepcopy(self.players)
            sorted_players = self.sorted_players[:]

            while game_not_found:
                game_players = []
                test_players = deepcopy(self.players)
                teammates_count = 0

                for _ in range(1, num + 1):
                    if elo_split:
                        elo_line = len(sorted_players) // 2
                        high_elo = sorted_players[:elo_line]
                        low_elo = sorted_players[elo_line:]
                        random.shuffle(high_elo)
                        random.shuffle(low_elo)
                        test_players = self.update_teammates(test_players, high_elo, low_elo)
                        test_players = self.update_opponents(test_players, high_elo, low_elo)
                        game_players.extend(high_elo + low_elo)
                    else:
                        random.shuffle(sorted_players)
                        test_players = self.update_teammates_single(test_players, sorted_players)
                        test_players = self.update_opponents_single(test_players, sorted_players)
                        game_players.extend(sorted_players)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                game_not_found = self.validate_games(num, teammates_count, test_players,
                                                     tolerance=elo_dif if not elo_split else None)

            self.players = test_players
            for i in range(1, num + 1):
                start_index = (i - 1) * 16
                end_index = i * 16
                current_game_players = game_players[start_index:end_index]
                self.print_game_schedule(f"Game {i + self.games_scheduled}", current_game_players)
            self.games_scheduled += num

        generate_single_type(num_split, elo_split=True)
        generate_single_type(num_based, elo_split=False)

    def validate_elo_based_games(self, num, teammates_count, test_players, sorted_players, team_tolerance):
        expected_teammates_count = num * len(self.sorted_players)
        if teammates_count == expected_teammates_count + self.previous_teammate_count:

            for i in range(1, num + 1):
                start_index = (i - 1) * 16
                end_index = i * 16

                current_sorted_players = sorted_players[start_index:end_index]
                current_tolerance = team_tolerance + ((i-1)*0.05)

                game1_match, game2_match, game3_match, game4_match = self.calculate_average(test_players,
                                                                                            current_sorted_players)
                if (game1_match <= current_tolerance and
                        game2_match <= current_tolerance and
                        game3_match <= current_tolerance and
                        game4_match <= current_tolerance):
                    for player in test_players.values():
                        for opponents, count in player.get_opponents().items():
                            if count > 2 or player.opponents_more_than_once() > 1:
                                return True
                            else:
                                continue
                    return False
                else:
                    return True
        else:
            return True
    def generate_elo_split_games(self, num):

        game_players = []
        game_not_found = True
        test_players = deepcopy(self.players)

        while game_not_found:
            game_players = []
            test_players = deepcopy(self.players)
            teammates_count = 0
            for _ in range(1, num + 1):
                elo_line = int(len(self.sorted_players) / 2)
                high_elo = self.sorted_players[:elo_line]
                low_elo = self.sorted_players[elo_line:]
                random.shuffle(high_elo)
                random.shuffle(low_elo)

                test_players = self.update_teammates(test_players, high_elo, low_elo)
                test_players = self.update_opponents(test_players, high_elo, low_elo)

                game_players = game_players + high_elo + low_elo

            for player in test_players.values():
                teammates_count += len(player.teammates)

            game_not_found = self.validate_elo_split_games(num, teammates_count, test_players)


        self.players = test_players
        for i in range(1, num + 1):
            start_index = (i - 1) * 16
            end_index = i * 16
            current_game_players = game_players[start_index:end_index]
            self.print_game_schedule(f"Game {i + self.games_scheduled}", current_game_players)


    def generate_elo_based_games(self, num, elo_dif):
        game_players = []
        sorted_players = self.sorted_players[:]
        game_not_found = True
        test_players = deepcopy(self.players)

        while game_not_found:
            game_players = []
            test_players = deepcopy(self.players)
            teammates_count = 0
            for _ in range(1, num + 1):
                random.shuffle(sorted_players)

                test_players = self.update_teammates_single(test_players, sorted_players)
                test_players = self.update_opponents_single(test_players, sorted_players)

                game_players = game_players + sorted_players

            for player in test_players.values():
                teammates_count += len(player.teammates)
            game_not_found = self.validate_elo_based_games(num, teammates_count, test_players, game_players, elo_dif)

        self.players = test_players
        for i in range(1, num + 1):
            start_index = (i - 1) * 16
            end_index = i * 16
            current_game_players = game_players[start_index:end_index]
            self.print_game_schedule(f"Game {i + self.games_scheduled}", current_game_players)
    def Game1(self):
        elo_line = int(len(self.sorted_players) / 2)
        high_elo = self.sorted_players[:elo_line]
        low_elo = self.sorted_players[elo_line:]
        random.shuffle(high_elo)
        random.shuffle(low_elo)
        game_num = 1
        expected_teammates_count = game_num * len(self.sorted_players)

        game_not_found = True
        test_players = self.players

        while game_not_found:
            try:
                random.shuffle(high_elo)
                random.shuffle(low_elo)
                teammates_count = 0

                test_players = deepcopy(self.players)
                test_players = self.update_teammates(test_players, high_elo, low_elo)
                test_players = self.update_opponents(test_players, high_elo, low_elo)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                if teammates_count == expected_teammates_count + self.previous_teammate_count:
                    for player in test_players.values():
                        for opponents, count in player.get_opponents().items():
                            if count > 1 or player.opponents_more_than_once() > 1:
                                raise BreakOut
                            else:
                                continue
                    game_not_found = False
            except BreakOut:
                pass

        self.players = test_players
        game_players = high_elo + low_elo
        self.game_players1 = [player.name for player in game_players]
        self.print_game_schedule("Game 1", high_elo + low_elo)
    def Game2(self):
        elo_line = int(len(self.sorted_players) / 2)
        high_elo = self.sorted_players[:elo_line]
        low_elo = self.sorted_players[elo_line:]
        game_num = 2
        expected_teammates_count = game_num * len(self.sorted_players)

        game_not_found = True
        test_players = self.players

        while game_not_found:
            try:
                random.shuffle(high_elo)
                random.shuffle(low_elo)
                teammates_count = 0

                test_players = deepcopy(self.players)
                test_players = self.update_teammates(test_players, high_elo, low_elo)
                test_players = self.update_opponents(test_players, high_elo, low_elo)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                if teammates_count == expected_teammates_count + self.previous_teammate_count:
                    for player in test_players.values():
                        for opponents, count in player.get_opponents().items():
                            if count > 1 or player.opponents_more_than_once() > 1:
                                raise BreakOut
                            else: continue
                    game_not_found = False
            except BreakOut:
                pass

        self.players = test_players
        game_players = high_elo + low_elo
        self.game_players2 = [player.name for player in game_players]
        self.print_game_schedule("Game 2", high_elo + low_elo)
    def Game3(self):
        game_players = self.sorted_players[:]

        game_num = 3
        expected_teammates_count = game_num * len(self.sorted_players)

        game_not_found = True
        team_tolerance = 1
        test_players = self.players

        while game_not_found:
            try:
                random.shuffle(game_players)
                teammates_count = 0

                test_players = deepcopy(self.players)
                test_players = self.update_teammates_single(test_players, game_players)
                test_players = self.update_opponents_single(test_players, game_players)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                if teammates_count == expected_teammates_count + self.previous_teammate_count:
                    game1_match, game2_match, game3_match, game4_match = self.calculate_average(test_players, game_players)
                    if (game1_match <= team_tolerance and
                            game2_match <= team_tolerance and
                            game3_match <= team_tolerance and
                            game4_match <= team_tolerance):
                        for player in test_players.values():
                            for opponents, count in player.get_opponents().items():
                                if count > 5 or player.opponents_more_than_once() > 1:
                                    raise BreakOut
                                else:
                                    continue
                        game_not_found = False
            except BreakOut:
                pass

        self.players = test_players
        self.game_players3 = [player.name for player in game_players]
        self.print_game_schedule("Game 3", game_players)
    def Game4(self):
        game_players = self.sorted_players[:]

        game_num = 4
        expected_teammates_count = game_num * len(self.sorted_players)

        game_not_found = True
        team_tolerance = 1
        test_players = self.players

        while game_not_found:
            try:
                random.shuffle(game_players)
                teammates_count = 0

                test_players = deepcopy(self.players)
                test_players = self.update_teammates_single(test_players, game_players)
                test_players = self.update_opponents_single(test_players, game_players)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                if teammates_count == expected_teammates_count + self.previous_teammate_count:
                    game1_match, game2_match, game3_match, game4_match = self.calculate_average(test_players, game_players)
                    if (game1_match <= team_tolerance and
                            game2_match <= team_tolerance and
                            game3_match <= team_tolerance and
                            game4_match <= team_tolerance):
                        for player in test_players.values():
                            for opponents, count in player.get_opponents().items():
                                if count > 5 or player.opponents_more_than_once() > 1:
                                    raise BreakOut
                                else:
                                    continue
                        game_not_found = False
            except BreakOut:
                pass

        self.players = test_players
        self.game_players4 = [player.name for player in game_players]
        self.print_game_schedule("Game 4", game_players)
    def Game5(self):
        game_players = self.sorted_players[:]

        game_num = 5
        expected_teammates_count = game_num * len(self.sorted_players)

        game_not_found = True
        team_tolerance = 1
        test_players = self.players

        while game_not_found:
            try:
                random.shuffle(game_players)
                teammates_count = 0

                test_players = deepcopy(self.players)
                test_players = self.update_teammates_single(test_players, game_players)
                test_players = self.update_opponents_single(test_players, game_players)

                for player in test_players.values():
                    teammates_count += len(player.teammates)

                if teammates_count == expected_teammates_count + self.previous_teammate_count:
                    game1_match, game2_match, game3_match, game4_match = self.calculate_average(test_players, game_players)
                    if (game1_match <= team_tolerance and
                            game2_match <= team_tolerance and
                            game3_match <= team_tolerance and
                            game4_match <= team_tolerance):
                        for player in test_players.values():
                            for opponents, count in player.get_opponents().items():
                                if count > 5:
                                    raise BreakOut
                                else:
                                    continue
                        game_not_found = False
            except BreakOut:
                pass

        self.players = test_players
        self.game_players5 = [player.name for player in game_players]
        self.print_game_schedule("Game 5", game_players)

    def create_game_csv(self, game_sets, filename="games.csv"):
        # Determine the number of games
        num_games = len(game_sets)

        # Open the CSV file for writing
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write the headers for each game
            headers = []
            for game_num in range(1, num_games + 1):
                headers.extend([f"Game {game_num}", ""])
            writer.writerow(headers)

            # Maximum number of teams per game set
            max_teams = max(len(game_set) // 4 for game_set in game_sets)

            for team_num in range(max_teams):
                row_team_names = []
                row_team_1 = []
                row_team_2 = []

                for game_set in game_sets:
                    self.replace_name(game_set, "Falcone", "Mike")
                    self.replace_name(game_set, "Baller", "Ballerini")
                    self.replace_name(game_set, "Steve", "Steven")
                    start_idx = team_num * 4
                    if start_idx + 3 < len(game_set):
                        row_1 = [game_set[start_idx], game_set[start_idx + 2]]
                        row_2 = [game_set[start_idx + 1], game_set[start_idx + 3]]

                        row_team_names.extend([f"Team {team_num * 2 + 1}", f"Team {team_num * 2 + 2}"])
                        row_team_1.extend(row_1)
                        row_team_2.extend(row_2)
                    else:
                        row_team_names.extend(["", ""])
                        row_team_1.extend(["", ""])
                        row_team_2.extend(["", ""])

                writer.writerow(row_team_names)
                writer.writerow(row_team_1)
                writer.writerow(row_team_2)
                writer.writerow(["", ""])  # Empty row for spacing

    def replace_name(self, players_list, old_name, new_name):
        for i, name in enumerate(players_list):
            if name == old_name:
                players_list[i] = new_name
                break