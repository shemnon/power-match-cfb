import argparse
from league import League
from scheduler import Scheduler
from simulator import Simulator
import config

def run_season(league, crossover_pairs, power_match_rounds, power_match_timing='mid'):
    scheduler = Scheduler(league)
    simulator = Simulator()
    played_game_ids = set()

    # Clear schedules (Stats are reset by caller if needed, or here if not)
    # Actually, for safety, let's ensure schedule is clear.
    # But we don't want to reset Elo here if we are evolving.
    # The caller handles reset_stats() which clears schedule/results.
    # But run_season is called in loop.
    # If we are NOT evolving, we create new League, so empty.
    # If we ARE evolving, we called reset_stats().
    # So we just need to ensure we don't double reset or miss it.
    # Let's just clear schedule list to be safe, but not stats if they weren't reset?
    # No, run_season implies a fresh season.
    # But we moved reset_stats to main loop for evolution.
    # Let's just trust the state passed in is ready, OR force a schedule clear.
    for t in league.teams:
        t.schedule = []
        # We do NOT reset wins/losses here because we might want to track them differently?
        # No, run_season should probably manage the season state.
        # But main loop does the regression.
        # Let's leave the stats reset to the main loop or ensure it's done.
        # For non-evolution, new League = clean stats.
        # For evolution, we called reset_stats.
        # So we are good.
        pass
    
    # Define Phases
    def play_phase_group():
        for group_id, teams in league.groups.items():
            n = len(teams)
            for i in range(n):
                for j in range(i + 1, n):
                     import random
                     is_home = random.choice([True, False])
                     teams[i].add_game(teams[j], is_home)
                     teams[j].add_game(teams[i], not is_home)
        play_scheduled_games(league, simulator, played_game_ids)

    def play_phase_crossover():
        for g1_id, g2_id in crossover_pairs:
            g1_teams = league.get_group(g1_id)
            g2_teams = league.get_group(g2_id)
            for t1 in g1_teams:
                for t2 in g2_teams:
                    import random
                    is_home = random.choice([True, False])
                    t1.add_game(t2, is_home)
                    t2.add_game(t1, not is_home)
        play_scheduled_games(league, simulator, played_game_ids)

    def play_phase_power_match():
        # power_match_rounds is a list of lists of pairs, e.g. [[('A', 'C'), ('B', 'D')], ...]
        for round_pairs in power_match_rounds:
            scheduler.schedule_power_match(round_pairs)
            play_scheduled_games(league, simulator, played_game_ids)

    # Execute based on timing
    # Execute based on timing
    if power_match_timing == 'mid':
        # Group -> Power Match -> Crossover
        play_phase_group()
        play_phase_power_match()
        play_phase_crossover()
    elif power_match_timing == 'end':
        # Group -> Crossover -> Power Match
        play_phase_group()
        play_phase_crossover()
        play_phase_power_match()

def run_chaos_season(league):
    scheduler = Scheduler(league)
    simulator = Simulator()
    played_game_ids = set()

    # Clear schedules
    for t in league.teams:
        t.schedule = []
        t.results = []
        t.wins = 0
        t.losses = 0
        t.points_for = 0
        t.points_against = 0

    # Generate full 9-game schedule
    scheduler.generate_chaos_schedule(num_games=9)
    
    # Play all games
    play_scheduled_games(league, simulator, played_game_ids)

def play_scheduled_games(league, simulator, played_games):
    """
    Plays games that are in the schedule but haven't been played.
    played_games: set of tuple(sorted_names)
    """
    for team in league.teams:
        for opponent, is_home in team.schedule:
            # Unique ID for game: sorted tuple of names
            game_id = tuple(sorted((team.name, opponent.name)))
            if game_id in played_games:
                continue
            
            # Play it
            simulator.simulate_game(team, opponent, is_home)
            played_games.add(game_id)

def analyze_tiebreakers(league):
    # Find top teams.
    # Sort by wins.
    standings = league.get_standings()
    
    # Check for ties at the top (for 2 spots)
    # If 2nd and 3rd place have same record, we have a tie for the CCG.
    
    if len(standings) < 3:
        return 0 # No tie possible
        
    p1 = standings[0]
    p2 = standings[1]
    p3 = standings[2]
    
    # Simple check: do p2 and p3 have same number of wins?
    if p2.wins == p3.wins:
        # Tie for 2nd place
        return 1
    
    # Check if p1 and p2 are tied (not a problem for CCG, but interesting)
    # Check if p1, p2, p3 all tied
    if p1.wins == p2.wins and p2.wins == p3.wins:
        return 1
        
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', choices=['SEC', 'BigXII'], default='SEC')
    parser.add_argument('--sims', type=int, default=1)
    parser.add_argument('--power-timing', choices=['mid', 'end'], default='mid', help='When to play Power Match games')
    parser.add_argument('--power-weeks', type=int, default=1, help='Number of Power Match weeks (1 or 2)')
    parser.add_argument('--model', choices=['group', 'chaos'], default='group', help='Scheduling model: group or chaos (9-game random)')
    parser.add_argument('--evolve-elo', action='store_true', help='Carry over Elo ratings between seasons (with regression)')
    args = parser.parse_args()

    if args.league == 'SEC':
        teams_data = config.SEC_TEAMS
        # Full Rotation (Crossover): A vs C, B vs D
        crossover_pairs = [('A', 'C'), ('B', 'D')]
        
        # Power Match Rounds:
        # Round 1: A hosts B, C hosts D
        # Round 2: A at D, B hosts C
        power_match_rounds = [
            [('A', 'B'), ('C', 'D')], # Week 1
            [('D', 'A'), ('B', 'C')]  # Week 2 (A at D means D is home)
        ]
    else:
        teams_data = config.BIG_XII_TEAMS
        crossover_pairs = [('A', 'C'), ('B', 'D')]
        power_match_rounds = [
            [('A', 'B'), ('C', 'D')],
            [('D', 'A'), ('B', 'C')]
        ]

    # If we only want 1 Power Match week (default), we just take the first list
    final_power_match_rounds = power_match_rounds[:args.power_weeks]

    tie_count = 0
    
    # Initialize league ONCE if evolving Elo
    league = None
    if args.evolve_elo:
        league = League(args.league, teams_data)

    for i in range(args.sims):
        if not args.evolve_elo:
            league = League(args.league, teams_data)
        else:
            # Reset stats but keep Elo
            # Apply regression to mean (soft reset)
            # New Elo = Old Elo * 0.75 + 1500 * 0.25
            for t in league.teams:
                t.elo = (t.elo * 0.75) + (1500 * 0.25)
                t.reset_stats()

        if args.model == 'chaos':
            run_chaos_season(league)
        else:
            run_season(league, crossover_pairs, final_power_match_rounds, power_match_timing=args.power_timing)
        
        if args.sims == 1:
            league.print_standings()
        
        if analyze_tiebreakers(league):
            tie_count += 1

    if args.sims > 1:
        print(f"\nSimulated {args.sims} seasons.")
        print(f"Seasons with a tie for the CCG spots (Top 2): {tie_count} ({tie_count/args.sims*100:.1f}%)")
    else:
        # Debug: check schedule length for Georgia
        ga = league.get_team('Georgia')
        if ga:
            print(f"Georgia Schedule ({len(ga.schedule)}): {[x[0].name for x in ga.schedule]}")
            print(f"Georgia Results ({len(ga.results)}): {[x[0] for x in ga.results]}")

if __name__ == "__main__":
    main()
