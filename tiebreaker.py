import re
import random
from league import League
import config

def parse_season_results(filename, league):
    """
    Parses the commentary output file to populate team results.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    # Regex for game result: "- Team A Score - Team B Score"
    # Example: "- Oklahoma State 12 - TCU 18"
    # Handling "Thriller!" or "UPSET!" at the end
    game_pattern = re.compile(r"- ([\w\s&]+) (\d+) - ([\w\s&]+) (\d+)")
    
    for line in lines:
        match = game_pattern.search(line)
        if match:
            team_a_name = match.group(1).strip()
            score_a = int(match.group(2))
            team_b_name = match.group(3).strip()
            score_b = int(match.group(4))
            
            # Find team objects
            team_a = next((t for t in league.teams if t.name == team_a_name), None)
            team_b = next((t for t in league.teams if t.name == team_b_name), None)
            
            if team_a and team_b:
                # Record result
                # Note: The Team class might record duplicates if we are not careful, 
                # but here we are starting fresh.
                team_a.record_result(team_b, score_a > score_b, score_a, score_b)
                team_b.record_result(team_a, score_b > score_a, score_b, score_a)

def get_common_opponents(teams):
    """
    Returns a set of opponent names that ALL teams in the list have played.
    """
    if not teams: return set()
    
    common = set([r[0] for r in teams[0].results])
    for t in teams[1:]:
        opponents = set([r[0] for r in t.results])
        common = common.intersection(opponents)
    return common

def get_win_pct_vs_opponents(team, opponent_names):
    wins = 0
    games = 0
    for opp_name, result, _ in team.results:
        if opp_name in opponent_names:
            games += 1
            if result == 'W':
                wins += 1
    return wins / games if games > 0 else 0

def get_strength_of_schedule(team, league):
    """
    Combined win percentage of conference opponents.
    """
    total_wins = 0
    total_games = 0
    for opp_name, _, _ in team.results:
        opp = next((t for t in league.teams if t.name == opp_name), None)
        if opp:
            total_wins += opp.wins
            total_games += len(opp.results)
            
    return total_wins / total_games if total_games > 0 else 0

def resolve_tie(tied_teams, league, rank_spot):
    """
    Resolves a tie among a list of teams for a specific rank spot.
    Returns the winner (or ordered list).
    """
    print(f"\nResolving {len(tied_teams)}-way tie for #{rank_spot}: {', '.join([t.name for t in tied_teams])}")
    
    candidates = list(tied_teams)
    
    # Step 1: Head-to-Head (Mini-League)
    print("Step 1: Head-to-Head (Mini-League)")
    # Calculate win % among tied teams
    h2h_records = {}
    for t in candidates:
        wins = 0
        games = 0
        tied_names = [x.name for x in candidates if x != t]
        for opp_name, result, _ in t.results:
            if opp_name in tied_names:
                games += 1
                if result == 'W': wins += 1
        pct = wins / games if games > 0 else 0
        h2h_records[t.name] = (wins, games, pct)
        
    # Sort by pct
    candidates.sort(key=lambda t: h2h_records[t.name][2], reverse=True)
    
    # Print H2H stats
    for t in candidates:
        r = h2h_records[t.name]
        print(f"  {t.name}: {r[0]}-{r[1]} ({r[2]:.3f})")
        
    # Filter top
    best_pct = h2h_records[candidates[0].name][2]
    survivors = [t for t in candidates if h2h_records[t.name][2] == best_pct]
    
    if len(survivors) == 1:
        print(f"  -> Winner: {survivors[0].name}")
        return survivors[0]
    elif len(survivors) < len(tied_teams):
        print(f"  -> Reduced to: {', '.join([t.name for t in survivors])}")
        # If we reduced the field but still have a tie, we RESTART with the survivors?
        # Big 12 rules say: "If one team defeated all other teams... that team is removed... remaining teams revert."
        # Or "If all tied teams did not play each other... move to next step."
        # Let's assume we continue with the survivors to the next step.
    else:
        print("  -> No separation.")
        
    candidates = survivors
    
    # Step 2: Record vs Common Opponents
    print("Step 2: Record vs Common Opponents")
    common_opps = get_common_opponents(candidates)
    if not common_opps:
        print("  -> No common opponents played by all.")
    else:
        print(f"  Common Opponents: {', '.join(common_opps)}")
        # Calculate pct
        cand_stats = []
        for t in candidates:
            pct = get_win_pct_vs_opponents(t, common_opps)
            cand_stats.append((t, pct))
        
        cand_stats.sort(key=lambda x: x[1], reverse=True)
        for t, pct in cand_stats:
            print(f"  {t.name}: {pct:.3f}")
            
        best_pct = cand_stats[0][1]
        survivors = [t for t, p in cand_stats if p == best_pct]
        
        if len(survivors) == 1:
            print(f"  -> Winner: {survivors[0].name}")
            return survivors[0]
        elif len(survivors) < len(candidates):
            print(f"  -> Reduced to: {', '.join([t.name for t in survivors])}")
            candidates = survivors
        else:
            print("  -> No separation.")

    # Step 3: Record vs Next Highest Placed Common Opponent
    # This requires a full league ranking. We are trying to determine the ranking!
    # We can use the current wins as a rough ranking.
    print("Step 3: Record vs Next Highest Placed Common Opponent")
    # Sort all league teams by wins
    league_standings = sorted(league.teams, key=lambda x: x.wins, reverse=True)
    
    for opp in league_standings:
        if opp in candidates: continue # Skip themselves
        
        # Check if this opponent is common to the survivors
        # Actually, the rule is "Record against the next highest placed common opponent".
        # So we check if ALL survivors played this opponent.
        
        all_played = True
        for t in candidates:
            played = any(r[0] == opp.name for r in t.results)
            if not played:
                all_played = False
                break
        
        if all_played:
            print(f"  Checking vs {opp.name} ({opp.wins} wins)...")
            # Compare results
            results = []
            for t in candidates:
                # Find result
                res = next((r[1] for r in t.results if r[0] == opp.name), None)
                results.append((t, 1 if res == 'W' else 0))
            
            # Check if anyone did better
            best_res = max(r[1] for r in results)
            worst_res = min(r[1] for r in results)
            
            if best_res > worst_res:
                # We have separation
                survivors = [t for t, r in results if r == best_res]
                print(f"    -> Separated! Winners: {', '.join([t.name for t in survivors])}")
                if len(survivors) == 1:
                    return survivors[0]
                candidates = survivors
                # Continue loop? Or restart? Usually continue down the list if still tied.
            else:
                print("    -> All tied.")
                
    # Step 4: Strength of Schedule
    print("Step 4: Strength of Schedule (Opponent Win %)")
    power_stats = []
    for t in candidates:
        power = get_strength_of_schedule(t, league)
        power_stats.append((t, power))
        
    power_stats.sort(key=lambda x: x[1], reverse=True)
    for t, power in power_stats:
        print(f"  {t.name}: {power:.4f}")
        
    best_power = power_stats[0][1]
    survivors = [t for t, s in power_stats if s == best_power]
    
    if len(survivors) == 1:
        print(f"  -> Winner: {survivors[0].name}")
        return survivors[0]
        
    candidates = survivors
    
    # Step 5: Coin Toss (Random)
    print("Step 5: Coin Toss")
    winner = random.choice(candidates)
    print(f"  -> Winner: {winner.name}")
    return winner

def main():
    # Initialize League
    teams_data = config.BIG_XII_TEAMS
    league = League("BigXII", teams_data)
    
    # Parse Results
    parse_season_results("commentary_output_big12.md", league)
    
    # Identify the 6-way tie for 2nd place (6-3 record)
    # Based on file: Texas Tech, Utah, Arizona State, Arizona, Kansas State, Cincinnati
    tied_names = ["Texas Tech", "Utah", "Arizona State", "Arizona", "Kansas State", "Cincinnati"]
    tied_teams = [t for t in league.teams if t.name in tied_names]
    
    # Verify records
    for t in tied_teams:
        print(f"{t.name}: {t.wins}-{t.losses}")
        
    # Resolve Tie
    winner = resolve_tie(tied_teams, league, 2)
    print(f"\nFinal Winner of the Tiebreaker (2nd Place): {winner.name}")

if __name__ == "__main__":
    main()
