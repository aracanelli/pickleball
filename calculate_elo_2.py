import math

class Games:
    def __init__(self):
        self.elo_const = 400
        self.base_k = 32
        self.k1_const = 100
        self.k2_const = 100
        self.k3_const = 100
        self.k4_const = 100

        self.team1 = []
        self.team1_elo = 0

        self.team2 = []
        self.team2_elo = 0

        self.E1 = 0.0
        self.E2 = 0.0

        self.winner_team_index = 0

    def set_team(self,  player1, player2, player3, player4):
        self.team1 = [player1, player2]
        self.team1_elo = (player1.elo + player2.elo) / 2
        self.team2 = [player3, player4]
        self.team2_elo = (player3.elo + player4.elo) / 2

        # Compute the expected result
        self.compute_expected_result()

    def compute_expected_result(self):
        self.E1 = 1.0 / (1.0 + 10.0 ** ((self.team1_elo - self.team2_elo) / self.elo_const))
        self.E2 = 1.0 / (1.0 + 10.0 ** ((self.team2_elo - self.team1_elo) / self.elo_const))

    def set_winner(self, score1, score2):
        self.winner_team_index = 1 if score1 > score2 else 2

        score_diff_factor = (score1 - score2) / 15

        self.k1_const = self.base_k * abs(score_diff_factor) * (self.team1_elo / self.team1[0].elo)
        self.k2_const = self.base_k * abs(score_diff_factor) * (self.team1_elo / self.team1[1].elo)
        self.k3_const = self.base_k * abs(score_diff_factor) * (self.team2_elo / self.team2[0].elo)
        self.k4_const = self.base_k * abs(score_diff_factor) * (self.team2_elo / self.team2[1].elo)

    def update_elo(self):
        if self.winner_team_index == 1:
            # you can even make your k_const stronger for the difference in points, you'd update your input to accept score difference
            self.team1[0].elo = self.team1[0].elo + self.k1_const * (1 - self.E1)
            self.team1[1].elo = self.team1[1].elo + self.k2_const * (1 - self.E1)
            self.team2[0].elo = self.team2[0].elo + self.k3_const * (0 - self.E2)
            self.team2[1].elo = self.team2[1].elo + self.k4_const * (0 - self.E2)

            self.team1[0].wins = self.team1[0].wins + 1
            self.team1[1].wins = self.team1[1].wins + 1
            self.team2[0].losses = self.team2[0].losses + 1
            self.team2[1].losses = self.team2[1].losses + 1
        elif self.winner_team_index == 2:
            self.team1[0].elo = self.team1[0].elo + self.k1_const * (1 - self.E1)
            self.team1[1].elo = self.team1[1].elo + self.k2_const * (1 - self.E1)
            self.team2[0].elo = self.team2[0].elo + self.k3_const * (0 - self.E2)
            self.team2[1].elo = self.team2[1].elo + self.k4_const * (0 - self.E2)

            self.team1[0].losses = self.team1[0].losses + 1
            self.team1[1].losses = self.team1[1].losses + 1
            self.team2[0].wins = self.team2[0].wins + 1
            self.team2[1].wins = self.team2[1].wins + 1


class Player:
    def __init__(self, id, name, sub=False):
        self.id = id
        self.name = name
        self.elo = 1000
        self.sub = sub
        self.wins = 0
        self.losses = 0