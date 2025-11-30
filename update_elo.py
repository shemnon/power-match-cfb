import re
import config

# Mapping from config names to Warren Nolan names (if different)
NAME_MAP = {
    'Miss State': 'Mississippi State',
    'Miami (FL)': 'Miami (FL)', # Example if needed
    'UCF': 'UCF',
    'BYU': 'BYU',
    'TCU': 'TCU',
    'LSU': 'LSU',
    'Ole Miss': 'Ole Miss',
    'USC': 'USC',
    'SMU': 'SMU',
    'UTSA': 'UTSA',
    'UAB': 'UAB',
    'UTEP': 'UTEP',
    'FAU': 'FAU',
    'FIU': 'FIU',
    'UNLV': 'UNLV',
    'UMass': 'UMass',
    'ULM': 'ULM',
    # Add others if they fail to match
}

def get_real_elo(html_content):
    team_elos = {}
    # Regex to find team name and then the Elo a few lines later
    # Pattern: <a class="blue-black" href="...">Team Name</a> ... <td ...>Record</td> ... <td ...>ELO</td>
    
    # We'll split by "name-subcontainer" to find teams
    chunks = html_content.split('class="name-subcontainer"')
    for chunk in chunks[1:]: # Skip first split before any team
        # Extract name
        name_match = re.search(r'>([^<]+)</a>', chunk)
        if not name_match:
            continue
        team_name = name_match.group(1).strip()
        
        # Extract Elo
        # The Elo is in the 2nd <td> after the name.
        # The first <td> after name is usually the closing </td> of the name cell, then next <td> is record, then next is Elo.
        # Let's find all <td ... >Value</td>
        
        td_matches = re.findall(r'<td[^>]*>\s*([^<]+)\s*</td>', chunk)
        # td_matches[0] might be record (e.g. 10-1)
        # td_matches[1] might be Elo (e.g. 1749.8)
        
        if len(td_matches) >= 2:
            try:
                elo_str = td_matches[1].strip()
                elo = float(elo_str)
                team_elos[team_name] = elo
            except ValueError:
                pass
                
    return team_elos

def update_config():
    with open('elo_page.html', 'r') as f:
        html = f.read()
        
    real_elos = get_real_elo(html)
    
    # Update SEC
    print("Updating SEC Teams...")
    for team in config.SEC_TEAMS:
        lookup_name = NAME_MAP.get(team['name'], team['name'])
        if lookup_name in real_elos:
            old_elo = team['elo']
            team['elo'] = real_elos[lookup_name]
            print(f"  {team['name']}: {old_elo} -> {team['elo']}")
        else:
            print(f"  WARNING: Could not find Elo for {team['name']} (looked for {lookup_name})")

    # Update Big XII
    print("\nUpdating Big XII Teams...")
    for team in config.BIG_XII_TEAMS:
        lookup_name = NAME_MAP.get(team['name'], team['name'])
        if lookup_name in real_elos:
            old_elo = team['elo']
            team['elo'] = real_elos[lookup_name]
            print(f"  {team['name']}: {old_elo} -> {team['elo']}")
        else:
            print(f"  WARNING: Could not find Elo for {team['name']} (looked for {lookup_name})")
            
    # Generate new config file content
    new_content = "# Elo ratings updated from Warren Nolan\n\n"
    new_content += f"SEC_TEAMS = {repr(config.SEC_TEAMS)}\n\n"
    new_content += f"BIG_XII_TEAMS = {repr(config.BIG_XII_TEAMS)}\n"
    
    # Format it nicely? repr() is ugly but valid python.
    # Let's try to format it a bit better or just write it.
    import pprint
    new_content = "# Elo ratings updated from Warren Nolan\n\n"
    new_content += "SEC_TEAMS = " + pprint.pformat(config.SEC_TEAMS, sort_dicts=False) + "\n\n"
    new_content += "BIG_XII_TEAMS = " + pprint.pformat(config.BIG_XII_TEAMS, sort_dicts=False) + "\n"
    
    with open('config.py', 'w') as f:
        f.write(new_content)
        
if __name__ == "__main__":
    update_config()
