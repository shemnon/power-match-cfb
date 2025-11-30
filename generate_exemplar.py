import argparse
from league import League
from scheduler import Scheduler
from simulator import Simulator
import config

def run_exemplar(league_name, power_match_timing):
    if league_name == 'SEC':
        teams_data = config.SEC_TEAMS
        crossover_pairs = [('A', 'C'), ('B', 'D')]
        power_rounds = [[('A', 'B'), ('C', 'D')], [('D', 'A'), ('B', 'C')]]
        power_match_rounds = [[('A', 'B'), ('C', 'D')], [('D', 'A'), ('B', 'C')]]
    else:
        teams_data = config.BIG_XII_TEAMS
        crossover_pairs = [('A', 'C'), ('B', 'D')]
        power_match_rounds = [[('A', 'B'), ('C', 'D')], [('D', 'A'), ('B', 'C')]]

    league = League(league_name, teams_data)
    scheduler = Scheduler(league)
    simulator = Simulator()
    
    # We want to capture the schedule structure.
    # We will simulate the season but print the "Weeks".
    
    print(f"\n### {league_name} Exemplar Schedule ({power_match_timing.upper()}-Season Power Match)")
    print("Format: Team (Record) vs Opponent (Record) [Result]")
    
    # Define phases and print them
    
    def print_phase(phase_name, games_played):
        print(f"\n#### {phase_name}")
        # We can't easily print "Week X" without tracking it per team, 
        # but we can print the set of games generated in this phase.
        # Since we simulate immediately in the main script, we can capture the results.
        # But for an exemplar, we want to see the matchups.
        
        # Let's group by team or just list all games?
        # Listing all games is too long (16 teams * 4 games = 32 games per phase).
        # Let's pick one team from each group to show their path.
        focus_teams = [league.get_group(g)[0] for g in sorted(league.groups.keys())]
        
        for t in focus_teams:
            # Find games added since last phase
            # t.schedule is list of (opp, home). t.results is list of results.
            # We assume they match index-wise.
            new_games_count = len(t.results) - games_played[t.name]
            if new_games_count > 0:
                recent_results = t.results[-new_games_count:]
                print(f"**{t.name}** ({t.group_id}): " + ", ".join([f"{r[1]} vs {r[0]}" for r in recent_results]))
                games_played[t.name] = len(t.results)

    games_played = {t.name: 0 for t in league.teams}
    played_game_ids = set()

    def play_and_print(phase_name):
        # We need to hook into the phase logic.
        # This duplicates logic from main.py, but that's okay for a display script.
        pass

    # Re-implement phase logic with printing
    
    # 1. Group
    for group_id, teams in league.groups.items():
        n = len(teams)
        for i in range(n):
            for j in range(i + 1, n):
                 import random
                 is_home = random.choice([True, False])
                 teams[i].add_game(teams[j], is_home)
                 teams[j].add_game(teams[i], not is_home)
    
    play_scheduled_games(league, simulator, played_game_ids)
    print_phase("Group Play (3 Games)", games_played)

    # 2. Power Match vs Crossover based on timing
    if power_match_timing == 'mid':
        # Power Match
        for round_idx, round_pairs in enumerate(power_match_rounds):
            scheduler.schedule_power_match(round_pairs)
            play_scheduled_games(league, simulator, played_game_ids)
            print_phase(f"Power Match Week {round_idx+1}", games_played)
            
        # Crossover
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
        print_phase("Crossover Play (4 Games)", games_played)
        
    else: # end
        # Crossover
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
        print_phase("Crossover Play (4 Games)", games_played)

        # Power Match
        for round_idx, round_pairs in enumerate(power_match_rounds):
            scheduler.schedule_power_match(round_pairs)
            play_scheduled_games(league, simulator, played_game_ids)
            print_phase(f"Power Match Week {round_idx+1}", games_played)

    # Final Standings
    print("\n**Final Standings**")
    league.print_standings()

def play_scheduled_games(league, simulator, played_games):
    for team in league.teams:
        for opponent, is_home in team.schedule:
            game_id = tuple(sorted((team.name, opponent.name)))
            if game_id in played_games:
                continue
            simulator.simulate_game(team, opponent, is_home)
            played_games.add(game_id)

if __name__ == "__main__":
    run_exemplar('SEC', 'mid')
    run_exemplar('SEC', 'end')
