import random

def get_capped_diff(team, games, cap=17):
    diff = 0
    for opp_name, result, score_diff in team.results:
        # Check if this game is in the set of games we care about
        # We need to match opponent name to the games list provided
        # This is a bit tricky with just strings.
        # Let's assume 'games' is a filter function or list of allowed opponent names.
        if games and opp_name not in games:
            continue
            
        # Apply cap
        if score_diff > cap: d = cap
        elif score_diff < -cap: d = -cap
        else: d = score_diff
        diff += d
    return diff

def rank_teams(teams, league_groups):
    """
    Recursive/Iterative ranking function.
    teams: List of Team objects to rank.
    league_groups: Dict of group_id -> list of all teams (for context).
    """
    if len(teams) <= 1:
        return teams

    # We need to find the best team (or worst) to separate them.
    # Standard procedure: Try to break the tie at the top.
    
    # Step 1: Conference Record (Total Wins)
    # We assume 'teams' are already tied at the previous level if we are here?
    # No, this is the top level entry.
    
    # Let's define the steps as functions that return a metric for a team.
    # Higher is better.
    
    def metric_conf_record(t):
        return t.wins # Total wins in simulation is conference record

    def metric_group_record(t):
        # Wins against own group
        wins = 0
        group_mates = [x.name for x in league_groups[t.group_id]]
        for opp_name, result, _ in t.results:
            if opp_name in group_mates and result == 'W':
                wins += 1
        return wins

    def metric_head_to_head(t, subset_teams):
        # Wins against the other teams in this specific tied subset
        wins = 0
        subset_names = [x.name for x in subset_teams if x != t]
        for opp_name, result, _ in t.results:
            if opp_name in subset_names and result == 'W':
                wins += 1
        return wins

    def metric_conf_diff(t):
        return get_capped_diff(t, None) # All games

    def metric_group_diff(t):
        group_mates = [x.name for x in league_groups[t.group_id]]
        return get_capped_diff(t, group_mates)

    def metric_random(t):
        return random.random()

    # The Hierarchy of Steps
    # For the "Restart" logic:
    # We apply a step.
    # If it separates the group into layers:
    #   Layer 1 (Best)
    #   Layer 2 ...
    #   Layer N (Worst)
    # If Layer 1 has 1 team -> That team is #1. Remove it. Restart ranking for the rest.
    # If Layer 1 has < Total teams -> We have reduced the pool. 
    #   BUT the user says "rankings re-start". 
    #   Usually this means: If we identify the top seed, we lock it in, then go back to Step 1 for the remaining teams.
    #   If we have a subset at the top still tied, we continue to Step 2 *for that subset*.
    
    # Let's implement a solver that takes a list of teams and returns the ordered list.
    
    sorted_teams = []
    remaining_teams = list(teams)
    
    while len(remaining_teams) > 0:
        if len(remaining_teams) == 1:
            sorted_teams.append(remaining_teams[0])
            break
            
        # Try to find the next best team
        # We run through the steps. If a step reduces the field of "candidates for #1", we keep going.
        # If a step leaves us with 1 candidate, we found it.
        
        candidates = list(remaining_teams)
        
        # Step 1: Conf Record
        candidates = filter_top_candidates(candidates, metric_conf_record)
        if len(candidates) == 1:
            winner = candidates[0]
            sorted_teams.append(winner)
            remaining_teams.remove(winner)
            continue
            
        # Step 2: Group Record
        candidates = filter_top_candidates(candidates, metric_group_record)
        if len(candidates) == 1:
            winner = candidates[0]
            sorted_teams.append(winner)
            remaining_teams.remove(winner)
            continue
            
        # Step 3: Head to Head (among the TIED candidates)
        # Note: H2H is tricky. If A>B, B>C, C>A (1-1 each), it doesn't separate.
        # If A>B, A>C (2-0), A wins.
        # We pass the full list of current candidates to the metric to calculate wins against *them*.
        candidates = filter_top_candidates(candidates, lambda t: metric_head_to_head(t, candidates))
        if len(candidates) == 1:
            winner = candidates[0]
            sorted_teams.append(winner)
            remaining_teams.remove(winner)
            continue
            
        # Step 4: Conf Diff
        candidates = filter_top_candidates(candidates, metric_conf_diff)
        if len(candidates) == 1:
            winner = candidates[0]
            sorted_teams.append(winner)
            remaining_teams.remove(winner)
            continue

        # Step 5: Group Diff
        candidates = filter_top_candidates(candidates, metric_group_diff)
        if len(candidates) == 1:
            winner = candidates[0]
            sorted_teams.append(winner)
            remaining_teams.remove(winner)
            continue
            
        # Step 6: Random
        candidates = filter_top_candidates(candidates, metric_random)
        winner = candidates[0]
        sorted_teams.append(winner)
        remaining_teams.remove(winner)
        
    return sorted_teams

def filter_top_candidates(teams, metric_func):
    """
    Returns the subset of teams that have the highest value for the metric.
    """
    if not teams: return []
    
    scored = [(t, metric_func(t)) for t in teams]
    # Sort descending
    scored.sort(key=lambda x: x[1], reverse=True)
    
    best_score = scored[0][1]
    # Return all teams with that score
    return [x[0] for x in scored if x[1] == best_score]

# --- Simulation of Scenarios ---

class MockTeam:
    def __init__(self, name, group_id):
        self.name = name
        self.group_id = group_id
        self.wins = 0
        self.results = [] # (opp_name, 'W'/'L', diff)
        
    def add_result(self, opp_name, result, diff):
        self.results.append((opp_name, result, diff))
        if result == 'W': self.wins += 1
        
    def __repr__(self):
        return self.name

def run_scenarios():
    print("--- Scenario 1: The Circle of Death (3-way tie for 1st) ---")
    # Group A: A, B, C, D
    # A beats B, B beats C, C beats A. All beat D.
    # All go 4-0 in crossover (just to isolate group tiebreakers).
    
    A = MockTeam('A', 'G1')
    B = MockTeam('B', 'G1')
    C = MockTeam('C', 'G1')
    D = MockTeam('D', 'G1')
    
    league_groups = {'G1': [A, B, C, D]}
    
    # A beats B (+7), L vs C (-7), W vs D (+20) -> 2-1 group
    # B beats C (+10), L vs A (-7), W vs D (+20) -> 2-1 group
    # C beats A (+7), L vs B (-10), W vs D (+20) -> 2-1 group
    # D loses all
    
    # Add Crossover wins (4 each)
    for t in [A, B, C]:
        t.wins = 6 # 2 group + 4 crossover
        # Add dummy crossover results
        for i in range(4): t.add_result(f"X{i}", 'W', 10)
        
    D.wins = 0
    
    # Group Games
    # A vs B: A wins +7
    A.add_result('B', 'W', 7)
    B.add_result('A', 'L', -7)
    
    # B vs C: B wins +10
    B.add_result('C', 'W', 10)
    C.add_result('B', 'L', -10)
    
    # C vs A: C wins +7
    C.add_result('A', 'W', 7)
    A.add_result('C', 'L', -7)
    
    # Vs D
    A.add_result('D', 'W', 20)
    B.add_result('D', 'W', 20)
    C.add_result('D', 'W', 20)
    D.add_result('A', 'L', -20)
    D.add_result('B', 'L', -20)
    D.add_result('C', 'L', -20)
    
    teams = [A, B, C, D]
    ranked = rank_teams(teams, league_groups)
    print(f"Rankings: {ranked}")
    print("Explanation:")
    print("1. Conf Record: A,B,C tied (6). D last.")
    print("2. Group Record: A,B,C tied (2-1).")
    print("3. H2H: A is 1-1 (vs B,C). B is 1-1. C is 1-1. Tied.")
    print("4. Conf Diff: All have +40 from crossover + group diff.")
    print("   A Group Diff: +7 -7 +17(cap) = +17")
    print("   B Group Diff: -7 +10 +17 = +20")
    print("   C Group Diff: +7 -10 +17 = +14")
    print("   -> B should be #1 based on Group Diff (if Conf Diff is tied)")
    
    # Let's verify logic trace
    # Step 4 Conf Diff:
    # A: 40 + 17 = 57
    # B: 40 + 20 = 60
    # C: 40 + 14 = 54
    # So B should be #1.
    # Then A vs C restart.
    # A vs C H2H: C beat A. So C should be #2?
    # Wait, restart means we go back to Step 1 for A and C.
    # Step 1: Tied. Step 2: Tied. Step 3 H2H: C beat A. C wins.
    # So Order: B, C, A.
    
    print(f"Result: {ranked[0].name} (1st), {ranked[1].name} (2nd), {ranked[2].name} (3rd)")

if __name__ == "__main__":
    run_scenarios()
