import argparse
import random
import config
from league import League
from scheduler import Scheduler
from simulator import Simulator

# Configuration
HOME_FIELD_ADVANTAGE = 10
POWER_MATCH_TIMING = 'mid' # or 'end'

def run_commentary_sim():
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', choices=['SEC', 'BigXII'], default='SEC')
    args = parser.parse_args()
    
    LEAGUE_NAME = args.league
    
    print(f"### {LEAGUE_NAME} Season Simulation (Commentary Mode - Static Elo)")
    print(f"Settings: HFA={HOME_FIELD_ADVANTAGE}, Power Match Timing={POWER_MATCH_TIMING.upper()}")
    
    # Setup
    if LEAGUE_NAME == 'SEC':
        teams_data = config.SEC_TEAMS
    else:
        teams_data = config.BIG_XII_TEAMS
        
    league = League(LEAGUE_NAME, teams_data)
    scheduler = Scheduler(league)
    simulator = Simulator()
    
    class CommentarySimulator(Simulator):
        def simulate_game(self, team_a, team_b, is_home_a):
            elo_a = team_a.elo + (HOME_FIELD_ADVANTAGE if is_home_a else 0)
            elo_b = team_b.elo + (HOME_FIELD_ADVANTAGE if not is_home_a else 0)
            prob_a = self.get_win_probability(elo_a, elo_b)
            
            # Determine winner
            if random.random() < prob_a:
                winner = team_a
                loser = team_b
                score_diff = int(random.expovariate(1/14)) + 1
                if score_diff > 50: score_diff = 50
            else:
                winner = team_b
                loser = team_a
                score_diff = int(random.expovariate(1/14)) + 1
                if score_diff > 50: score_diff = 50
                
            # Update Elo - DISABLED for this run
            # team_a.elo += ...
            # team_b.elo += ...
            
            # Record result
            loser_score = random.randint(10, 30)
            winner_score = loser_score + score_diff
            
            score_a = winner_score if winner == team_a else loser_score
            score_b = winner_score if winner == team_b else loser_score
            
            team_a.record_result(team_b, winner == team_a, score_a, score_b)
            team_b.record_result(team_a, winner == team_b, score_b, score_a)
            
            # Commentary String
            upset = ""
            if (prob_a > 0.7 and winner == team_b) or (prob_a < 0.3 and winner == team_a):
                upset = " **UPSET!**"
            elif score_diff < 4:
                upset = " *Thriller!*"
                
            print(f"- {team_a.name} {score_a} - {team_b.name} {score_b}{upset}")
            return winner

    sim = CommentarySimulator()

    def play_batch(games_list, phase_name):
        print(f"\n#### {phase_name}")
        random.shuffle(games_list)
        for t1, t2, is_home in games_list:
            sim.simulate_game(t1, t2, is_home)

    # 1. Group Games (3 Weeks)
    # Structured Round Robin
    # Week 1: 0v1, 2v3
    # Week 2: 0v2, 1v3
    # Week 3: 0v3, 1v2
    
    weeks_group = [[], [], []]
    
    for group_id, teams in league.groups.items():
        # teams is list of 4
        # Week 1
        weeks_group[0].append((teams[0], teams[1], random.choice([True, False])))
        weeks_group[0].append((teams[2], teams[3], random.choice([True, False])))
        
        # Week 2
        weeks_group[1].append((teams[0], teams[2], random.choice([True, False])))
        weeks_group[1].append((teams[1], teams[3], random.choice([True, False])))
        
        # Week 3
        weeks_group[2].append((teams[0], teams[3], random.choice([True, False])))
        weeks_group[2].append((teams[1], teams[2], random.choice([True, False])))
        
    for i, games in enumerate(weeks_group):
        play_batch(games, f"Week {i+1}: Group Play")

    print("\n**Standings after Group Play**")
    league.print_standings()

    # 2. Power Match (Mid Season) - Weeks 4 & 5
    # Same logic as before
    power_match_games_w1 = []
    # A vs B (A Home)
    gA = league.get_group('A')
    gB = league.get_group('B')
    gA_sorted = sorted(gA, key=lambda x: (x.wins, x.elo), reverse=True)
    gB_sorted = sorted(gB, key=lambda x: (x.wins, x.elo), reverse=True)
    for i in range(4):
        power_match_games_w1.append((gA_sorted[i], gB_sorted[i], True))
        
    # C vs D (C Home)
    gC = league.get_group('C')
    gD = league.get_group('D')
    gC_sorted = sorted(gC, key=lambda x: (x.wins, x.elo), reverse=True)
    gD_sorted = sorted(gD, key=lambda x: (x.wins, x.elo), reverse=True)
    for i in range(4):
        power_match_games_w1.append((gC_sorted[i], gD_sorted[i], True))
        
    play_batch(power_match_games_w1, "Week 4: Power Match (A hosts B, C hosts D)")

    power_match_games_w2 = []
    # A at D (D Home)
    gA_sorted = sorted(gA, key=lambda x: (x.wins, x.elo), reverse=True) # Re-sort!
    gD_sorted = sorted(gD, key=lambda x: (x.wins, x.elo), reverse=True)
    for i in range(4):
        power_match_games_w2.append((gA_sorted[i], gD_sorted[i], False)) # A is Away
        
    # B hosts C (B Home)
    gB_sorted = sorted(gB, key=lambda x: (x.wins, x.elo), reverse=True)
    gC_sorted = sorted(gC, key=lambda x: (x.wins, x.elo), reverse=True)
    for i in range(4):
        power_match_games_w2.append((gB_sorted[i], gC_sorted[i], True))

    play_batch(power_match_games_w2, "Week 5: Power Match (D hosts A, B hosts C)")
    
    print("\n**Standings after Power Match Weeks**")
    league.print_standings()

    # 3. Crossover (4 Weeks) - Weeks 6-9
    # A vs C, B vs D
    # We need to rotate them so everyone plays everyone in the other group.
    # Group A: A0, A1, A2, A3
    # Group C: C0, C1, C2, C3
    # Week 6: A0-C0, A1-C1, A2-C2, A3-C3
    # Week 7: A0-C1, A1-C2, A2-C3, A3-C0
    # Week 8: A0-C2, A1-C3, A2-C0, A3-C1
    # Week 9: A0-C3, A1-C0, A2-C1, A3-C2
    
    weeks_crossover = [[], [], [], []]
    
    pairs = [('A', 'C'), ('B', 'D')]
    
    for g1_id, g2_id in pairs:
        g1 = league.get_group(g1_id)
        g2 = league.get_group(g2_id)
        n = 4
        for w in range(4):
            for i in range(n):
                t1 = g1[i]
                t2 = g2[(i + w) % n]
                is_home = random.choice([True, False])
                weeks_crossover[w].append((t1, t2, is_home))
                
    for i, games in enumerate(weeks_crossover):
        play_batch(games, f"Week {i+6}: Crossover Play")

    print("\n### Final Regular Season Standings")
    league.print_standings()

if __name__ == "__main__":
    run_commentary_sim()
