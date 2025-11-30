import random

class Team:
    def __init__(self, name, group_id, initial_elo=1500):
        self.name = name
        self.group_id = group_id
        self.elo = initial_elo
        self.wins = 0
        self.losses = 0
        self.schedule = [] # List of (opponent_team_obj, is_home)
        self.results = [] # List of (opponent_name, result_str, score_diff)
        self.points_for = 0
        self.points_against = 0

    def add_game(self, opponent, is_home=True):
        self.schedule.append((opponent, is_home))

    def record_result(self, opponent, won, score_for, score_against):
        if won:
            self.wins += 1
            result = 'W'
        else:
            self.losses += 1
            result = 'L'
        
        self.points_for += score_for
        self.points_against += score_against
        self.results.append((opponent.name, result, score_for - score_against))

    def reset_stats(self):
        self.wins = 0
        self.losses = 0
        self.schedule = []
        self.results = []
        self.points_for = 0
        self.points_against = 0

    def get_record(self):
        return f"{self.wins}-{self.losses}"

    def __repr__(self):
        return f"{self.name} ({self.get_record()}) Elo: {self.elo:.0f}"
