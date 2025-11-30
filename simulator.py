import random
import math

class Simulator:
    def __init__(self, k_factor=32):
        self.k_factor = k_factor

    def get_win_probability(self, elo_a, elo_b):
        return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

    def simulate_game(self, team_a, team_b, is_home_a):
        # Home field advantage
        home_field_advantage = 50
        elo_a = team_a.elo + (home_field_advantage if is_home_a else 0)
        elo_b = team_b.elo + (home_field_advantage if not is_home_a else 0)

        prob_a = self.get_win_probability(elo_a, elo_b)
        
        # Determine winner
        if random.random() < prob_a:
            winner = team_a
            loser = team_b
            score_diff = int(random.expovariate(1/14)) + 1 # Simple score diff model
            if score_diff > 50: score_diff = 50
        else:
            winner = team_b
            loser = team_a
            score_diff = int(random.expovariate(1/14)) + 1
            if score_diff > 50: score_diff = 50

        # Update Elo
        # Actual score: 1 for win, 0 for loss
        actual_score_a = 1 if winner == team_a else 0
        actual_score_b = 1 if winner == team_b else 0
        
        # Recalculate prob without HFA for permanent rating update? 
        # Usually Elo includes HFA in the prediction but updates based on the result.
        # We'll stick to the prediction used for the game.
        
        team_a.elo += self.k_factor * (actual_score_a - prob_a)
        team_b.elo += self.k_factor * (actual_score_b - (1 - prob_a))

        # Record stats
        # Just making up scores for display, e.g. Winner 28, Loser 28-diff
        loser_score = random.randint(0, 30)
        winner_score = loser_score + score_diff
        
        score_a = winner_score if winner == team_a else loser_score
        score_b = winner_score if winner == team_b else loser_score

        team_a.record_result(team_b, winner == team_a, score_a, score_b)
        team_b.record_result(team_a, winner == team_b, score_b, score_a)

        return winner
