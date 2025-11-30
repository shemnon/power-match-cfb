import config
from league import League

def analyze_balance(league_name, teams_data):
    league = League(league_name, teams_data)
    print(f"\n### {league_name} Group Balance Analysis")
    
    group_stats = []
    
    for group_id, teams in league.groups.items():
        avg_elo = sum(t.elo for t in teams) / len(teams)
        max_elo = max(t.elo for t in teams)
        min_elo = min(t.elo for t in teams)
        spread = max_elo - min_elo
        
        group_stats.append({
            'id': group_id,
            'avg': avg_elo,
            'max': max_elo,
            'min': min_elo,
            'spread': spread,
            'teams': [t.name for t in teams]
        })
        
    # Sort by Average Elo (Strongest to Weakest)
    group_stats.sort(key=lambda x: x['avg'], reverse=True)
    
    for g in group_stats:
        print(f"**Group {g['id']}** (Avg Elo: {g['avg']:.1f})")
        print(f"  - Teams: {', '.join(g['teams'])}")
        print(f"  - Range: {g['min']} - {g['max']} (Spread: {g['spread']})")
        print()

if __name__ == "__main__":
    analyze_balance("SEC", config.SEC_TEAMS)
    analyze_balance("Big XII", config.BIG_XII_TEAMS)
