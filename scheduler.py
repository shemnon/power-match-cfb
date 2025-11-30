import random

class Scheduler:
    def __init__(self, league):
        self.league = league

    def generate_schedule(self, crossover_pairs):
        """
        crossover_pairs: List of tuples (group_id_1, group_id_2) indicating which groups play full crossover.
        The remaining groups will be used for power match if possible.
        """
        
        # 1. Intra-group Round Robin
        for group_id, teams in self.league.groups.items():
            n = len(teams)
            for i in range(n):
                for j in range(i + 1, n):
                    # Simple home/away alternation could be better, but random for now
                    is_home = random.choice([True, False])
                    teams[i].add_game(teams[j], is_home)
                    teams[j].add_game(teams[i], not is_home)

        # 2. Cross-over Round Robin
        # crossover_pairs e.g., [('A', 'B'), ('C', 'D')]
        for g1_id, g2_id in crossover_pairs:
            g1_teams = self.league.get_group(g1_id)
            g2_teams = self.league.get_group(g2_id)
            
            for t1 in g1_teams:
                for t2 in g2_teams:
                    is_home = random.choice([True, False])
                    t1.add_game(t2, is_home)
                    t2.add_game(t1, not is_home)

    def schedule_power_match(self, matchup_groups):
        """
        matchup_groups: List of tuples (home_group_id, away_group_id).
        """
        for g1_id, g2_id in matchup_groups:
            g1_teams = self.league.get_group(g1_id)
            g2_teams = self.league.get_group(g2_id)
            
            # Sort groups by current record/elo to find 1v1, 2v2, etc.
            g1_sorted = sorted(g1_teams, key=lambda x: (x.wins, x.elo), reverse=True)
            g2_sorted = sorted(g2_teams, key=lambda x: (x.wins, x.elo), reverse=True)
            
            for i in range(min(len(g1_sorted), len(g2_sorted))):
                t1 = g1_sorted[i] # Home
                t2 = g2_sorted[i] # Away
                is_home = True
                t1.add_game(t2, is_home)
                t2.add_game(t1, not is_home)

    def generate_chaos_schedule(self, num_games=9):
        """
        Generates a random schedule where every team plays 'num_games' opponents.
        This is equivalent to generating a random k-regular graph.
        """
        teams = self.league.teams
        n = len(teams)
        
        # Try to generate a valid graph. If we get stuck, restart.
        max_retries = 100
        for attempt in range(max_retries):
            # Reset schedules for this attempt
            for t in teams:
                t.schedule = []
            
            # Track degrees
            degrees = {t.name: 0 for t in teams}
            
            # Create a pool of needed edges? 
            # Better: Iterate through teams and try to fill their schedule.
            # Or: Create a list of "stubs" [t1, t1, ..., t2, t2, ...] and shuffle/pair?
            # The configuration model (stubs) can create self-loops and multi-edges.
            # Let's try a simple randomized greedy approach.
            
            success = True
            # Create all possible pairs
            all_pairs = []
            for i in range(n):
                for j in range(i + 1, n):
                    all_pairs.append((teams[i], teams[j]))
            
            random.shuffle(all_pairs)
            
            for t1, t2 in all_pairs:
                if degrees[t1.name] < num_games and degrees[t2.name] < num_games:
                    # Add edge
                    is_home = random.choice([True, False])
                    t1.add_game(t2, is_home)
                    t2.add_game(t1, not is_home)
                    degrees[t1.name] += 1
                    degrees[t2.name] += 1
            
            # Check if everyone has num_games
            if all(d == num_games for d in degrees.values()):
                return # Success!
            
            # If not, we failed this attempt (greedy approach got stuck)
            # print(f"Retry chaos schedule generation... {attempt}")
            
        raise Exception("Failed to generate valid chaos schedule after multiple attempts.")

