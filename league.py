from team import Team

class League:
    def __init__(self, name, teams_data):
        """
        teams_data: List of dicts with 'name', 'group_id', 'elo'
        """
        self.name = name
        self.teams = []
        self.groups = {} # group_id -> list of Team objects

        for t_data in teams_data:
            team = Team(t_data['name'], t_data['group_id'], t_data.get('elo', 1500))
            self.teams.append(team)
            if team.group_id not in self.groups:
                self.groups[team.group_id] = []
            self.groups[team.group_id].append(team)

    def get_team(self, name):
        for team in self.teams:
            if team.name == name:
                return team
        return None

    def get_group(self, group_id):
        return self.groups.get(group_id, [])

    def get_standings(self):
        # Sort by wins (desc), then Elo (desc) as a simple proxy for now
        return sorted(self.teams, key=lambda x: (x.wins, x.elo), reverse=True)

    def print_standings(self):
        print(f"--- {self.name} Standings ---")
        for team in self.get_standings():
            print(f"{team.name:<20} {team.get_record()}  Elo: {team.elo:.0f}")
