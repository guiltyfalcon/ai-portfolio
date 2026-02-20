"""
Sports Data - Auto-Updated Weekly via Cron
Last Updated: 2026-02-19
Sources: nba_api (NBA free), ESPN/curated (NFL/MLB/NHL)
"""

# ============ NBA PLAYERS ============
NBA_TEAMS = {
    'LAL': [
        {'name': 'LeBron James', 'ppg': 25.2, 'rpg': 7.8, 'apg': 9.0, 'fg_pct': 0.52},
        {'name': 'Anthony Davis', 'ppg': 24.8, 'rpg': 12.5, 'apg': 3.5, 'fg_pct': 0.55},
        {'name': 'Austin Reaves', 'ppg': 15.8, 'rpg': 4.2, 'apg': 5.1, 'fg_pct': 0.48},
        {'name': "D'Angelo Russell", 'ppg': 14.2, 'rpg': 3.1, 'apg': 6.0, 'fg_pct': 0.45},
    ],
    'GSW': [
        {'name': 'Stephen Curry', 'ppg': 28.5, 'rpg': 4.4, 'apg': 5.1, 'fg_pct': 0.47},
        {'name': 'Klay Thompson', 'ppg': 18.2, 'rpg': 3.5, 'apg': 2.3, 'fg_pct': 0.43},
        {'name': 'Draymond Green', 'ppg': 8.5, 'rpg': 7.2, 'apg': 6.8, 'fg_pct': 0.49},
        {'name': 'Andrew Wiggins', 'ppg': 13.8, 'rpg': 4.5, 'apg': 1.7, 'fg_pct': 0.46},
    ],
    'BOS': [
        {'name': 'Jayson Tatum', 'ppg': 27.2, 'rpg': 8.3, 'apg': 4.9, 'fg_pct': 0.48},
        {'name': 'Jaylen Brown', 'ppg': 23.5, 'rpg': 5.6, 'apg': 3.4, 'fg_pct': 0.49},
        {'name': 'Kristaps Porzingis', 'ppg': 20.1, 'rpg': 7.2, 'apg': 2.0, 'fg_pct': 0.51},
        {'name': 'Derrick White', 'ppg': 15.2, 'rpg': 4.0, 'apg': 5.2, 'fg_pct': 0.46},
    ],
    'DEN': [
        {'name': 'Nikola Jokic', 'ppg': 25.9, 'rpg': 12.0, 'apg': 9.1, 'fg_pct': 0.58},
        {'name': 'Jamal Murray', 'ppg': 21.2, 'rpg': 4.1, 'apg': 6.5, 'fg_pct': 0.48},
        {'name': 'Aaron Gordon', 'ppg': 13.8, 'rpg': 6.5, 'apg': 3.2, 'fg_pct': 0.56},
        {'name': 'Michael Porter Jr', 'ppg': 16.5, 'rpg': 7.0, 'apg': 1.5, 'fg_pct': 0.48},
    ],
    'PHX': [
        {'name': 'Kevin Durant', 'ppg': 29.1, 'rpg': 6.7, 'apg': 5.0, 'fg_pct': 0.53},
        {'name': 'Devin Booker', 'ppg': 27.8, 'rpg': 4.5, 'apg': 6.9, 'fg_pct': 0.49},
        {'name': 'Bradley Beal', 'ppg': 18.2, 'rpg': 4.0, 'apg': 4.5, 'fg_pct': 0.51},
        {'name': 'Jusuf Nurkic', 'ppg': 11.0, 'rpg': 11.0, 'apg': 4.0, 'fg_pct': 0.52},
    ],
    'MIL': [
        {'name': 'Giannis Antetokounmpo', 'ppg': 30.8, 'rpg': 11.5, 'apg': 6.5, 'fg_pct': 0.61},
        {'name': 'Damian Lillard', 'ppg': 24.8, 'rpg': 4.4, 'apg': 7.0, 'fg_pct': 0.43},
        {'name': 'Khris Middleton', 'ppg': 15.2, 'rpg': 4.8, 'apg': 5.1, 'fg_pct': 0.47},
        {'name': 'Brook Lopez', 'ppg': 12.8, 'rpg': 4.9, 'apg': 1.3, 'fg_pct': 0.46},
    ],
    'DAL': [
        {'name': 'Luka Doncic', 'ppg': 33.8, 'rpg': 9.2, 'apg': 9.8, 'fg_pct': 0.48},
        {'name': 'Kyrie Irving', 'ppg': 25.2, 'rpg': 5.0, 'apg': 5.2, 'fg_pct': 0.49},
        {'name': 'PJ Washington', 'ppg': 11.5, 'rpg': 6.8, 'apg': 1.2, 'fg_pct': 0.44},
        {'name': 'Dereck Lively II', 'ppg': 8.8, 'rpg': 7.2, 'apg': 1.1, 'fg_pct': 0.75},
    ],
    'NYK': [
        {'name': 'Jalen Brunson', 'ppg': 28.5, 'rpg': 3.6, 'apg': 6.5, 'fg_pct': 0.48},
        {'name': 'Julius Randle', 'ppg': 24.0, 'rpg': 9.2, 'apg': 5.0, 'fg_pct': 0.47},
        {'name': 'RJ Barrett', 'ppg': 20.2, 'rpg': 5.0, 'apg': 3.0, 'fg_pct': 0.44},
        {'name': 'OG Anunoby', 'ppg': 14.5, 'rpg': 4.2, 'apg': 1.4, 'fg_pct': 0.49},
    ],
    'MIA': [
        {'name': 'Jimmy Butler', 'ppg': 21.0, 'rpg': 5.5, 'apg': 5.2, 'fg_pct': 0.47},
        {'name': 'Bam Adebayo', 'ppg': 20.2, 'rpg': 10.5, 'apg': 4.0, 'fg_pct': 0.52},
        {'name': 'Tyler Herro', 'ppg': 20.8, 'rpg': 5.3, 'apg': 4.4, 'fg_pct': 0.44},
        {'name': 'Duncan Robinson', 'ppg': 12.5, 'rpg': 2.8, 'apg': 2.5, 'fg_pct': 0.43},
    ],
    'PHI': [
        {'name': 'Joel Embiid', 'ppg': 34.2, 'rpg': 11.2, 'apg': 5.8, 'fg_pct': 0.54},
        {'name': 'Tyrese Maxey', 'ppg': 25.5, 'rpg': 3.7, 'apg': 6.2, 'fg_pct': 0.45},
        {'name': 'Tobias Harris', 'ppg': 17.2, 'rpg': 6.4, 'apg': 3.1, 'fg_pct': 0.48},
        {'name': 'Kelly Oubre Jr', 'ppg': 15.5, 'rpg': 5.0, 'apg': 1.5, 'fg_pct': 0.45},
    ],
}

# ============ NFL PLAYERS ============
NFL_TEAMS = {
    'KC': [
        {'name': 'Patrick Mahomes', 'pass_yds': 268, 'pass_td': 2.0, 'rush_yds': 22, 'rush_td': 0.2},
        {'name': 'Travis Kelce', 'rec': 6.2, 'rec_yds': 76, 'rec_td': 0.6, 'rush_yds': 0},
        {'name': 'Rashee Rice', 'rec': 5.2, 'rec_yds': 62, 'rec_td': 0.4, 'rush_yds': 8},
        {'name': 'Isiah Pacheco', 'rush': 16, 'rush_yds': 72, 'rush_td': 0.5, 'rec': 2.2},
    ],
    'SF': [
        {'name': 'Brock Purdy', 'pass_yds': 258, 'pass_td': 1.8, 'rush_yds': 15, 'rush_td': 0.1},
        {'name': 'Christian McCaffrey', 'rush': 17, 'rush_yds': 82, 'rush_td': 0.7, 'rec': 4.2, 'rec_yds': 38},
        {'name': 'Deebo Samuel', 'rec': 4.8, 'rec_yds': 72, 'rec_td': 0.4, 'rush': 3.2, 'rush_yds': 18},
        {'name': 'George Kittle', 'rec': 4.2, 'rec_yds': 58, 'rec_td': 0.4, 'rush_yds': 0},
    ],
    'BAL': [
        {'name': 'Lamar Jackson', 'pass_yds': 228, 'pass_td': 1.7, 'rush_yds': 62, 'rush_td': 0.5},
        {'name': 'Derrick Henry', 'rush': 21, 'rush_yds': 108, 'rush_td': 0.9, 'rec': 1.2, 'rec_yds': 8},
        {'name': 'Zay Flowers', 'rec': 5.5, 'rec_yds': 68, 'rec_td': 0.3, 'rush_yds': 5},
        {'name': 'Mark Andrews', 'rec': 4.2, 'rec_yds': 52, 'rec_td': 0.4, 'rush_yds': 0},
    ],
    'BUF': [
        {'name': 'Josh Allen', 'pass_yds': 252, 'pass_td': 2.1, 'rush_yds': 48, 'rush_td': 0.6},
        {'name': 'Stefon Diggs', 'rec': 5.8, 'rec_yds': 72, 'rec_td': 0.5, 'rush_yds': 2},
        {'name': 'James Cook', 'rush': 12, 'rush_yds': 48, 'rush_td': 0.3, 'rec': 4.2, 'rec_yds': 35},
        {'name': 'Dalton Kincaid', 'rec': 4.5, 'rec_yds': 45, 'rec_td': 0.3, 'rush_yds': 0},
    ],
}

# ============ MLB PLAYERS ============
MLB_TEAMS = {
    'LAD': [
        {'name': 'Shohei Ohtani', 'avg': 0.302, 'hr': 0.26, 'rbi': 0.82, 'hits': 1.2},
        {'name': 'Mookie Betts', 'avg': 0.275, 'hr': 0.20, 'rbi': 0.68, 'hits': 1.0},
        {'name': 'Freddie Freeman', 'avg': 0.295, 'hr': 0.18, 'rbi': 0.78, 'hits': 1.1},
        {'name': 'Will Smith', 'avg': 0.262, 'hr': 0.16, 'rbi': 0.58, 'hits': 0.9},
    ],
    'NYY': [
        {'name': 'Aaron Judge', 'avg': 0.280, 'hr': 0.32, 'rbi': 0.88, 'hits': 1.0},
        {'name': 'Juan Soto', 'avg': 0.285, 'hr': 0.22, 'rbi': 0.78, 'hits': 1.1},
        {'name': 'Giancarlo Stanton', 'avg': 0.245, 'hr': 0.28, 'rbi': 0.78, 'hits': 0.9},
        {'name': 'Gleyber Torres', 'avg': 0.272, 'hr': 0.15, 'rbi': 0.58, 'hits': 1.0},
    ],
    'ATL': [
        {'name': 'Ronald Acuna Jr', 'avg': 0.290, 'hr': 0.20, 'rbi': 0.62, 'hits': 1.1},
        {'name': 'Matt Olson', 'avg': 0.268, 'hr': 0.26, 'rbi': 0.82, 'hits': 1.0},
        {'name': 'Austin Riley', 'avg': 0.285, 'hr': 0.24, 'rbi': 0.82, 'hits': 1.0},
        {'name': 'Marcell Ozuna', 'avg': 0.280, 'hr': 0.25, 'rbi': 0.85, 'hits': 1.0},
    ],
    'HOU': [
        {'name': 'Yordan Alvarez', 'avg': 0.290, 'hr': 0.28, 'rbi': 0.88, 'hits': 1.0},
        {'name': 'Jose Altuve', 'avg': 0.298, 'hr': 0.16, 'rbi': 0.62, 'hits': 1.2},
        {'name': 'Kyle Tucker', 'avg': 0.285, 'hr': 0.22, 'rbi': 0.78, 'hits': 1.0},
        {'name': 'Alex Bregman', 'avg': 0.265, 'hr': 0.18, 'rbi': 0.68, 'hits': 0.9},
    ],
}

# ============ NHL PLAYERS ============
NHL_TEAMS = {
    'COL': [
        {'name': 'Nathan MacKinnon', 'goals': 0.50, 'assists': 0.85, 'points': 1.35, 'shots': 4.3},
        {'name': 'Cale Makar', 'goals': 0.26, 'assists': 0.68, 'points': 0.94, 'shots': 3.0},
        {'name': 'Mikko Rantanen', 'goals': 0.40, 'assists': 0.58, 'points': 0.98, 'shots': 3.6},
        {'name': 'Valeri Nichushkin', 'goals': 0.33, 'assists': 0.42, 'points': 0.75, 'shots': 2.6},
    ],
    'EDM': [
        {'name': 'Connor McDavid', 'goals': 0.52, 'assists': 1.02, 'points': 1.54, 'shots': 4.0},
        {'name': 'Leon Draisaitl', 'goals': 0.48, 'assists': 0.68, 'points': 1.16, 'shots': 3.2},
        {'name': 'Zach Hyman', 'goals': 0.42, 'assists': 0.40, 'points': 0.82, 'shots': 2.8},
        {'name': 'Ryan Nugent-Hopkins', 'goals': 0.26, 'assists': 0.52, 'points': 0.78, 'shots': 2.2},
    ],
    'TOR': [
        {'name': 'Auston Matthews', 'goals': 0.68, 'assists': 0.45, 'points': 1.13, 'shots': 3.8},
        {'name': 'Mitch Marner', 'goals': 0.32, 'assists': 0.78, 'points': 1.10, 'shots': 2.6},
        {'name': 'William Nylander', 'goals': 0.40, 'assists': 0.55, 'points': 0.95, 'shots': 3.3},
        {'name': 'John Tavares', 'goals': 0.35, 'assists': 0.45, 'points': 0.80, 'shots': 2.6},
    ],
    'NYR': [
        {'name': 'Artemi Panarin', 'goals': 0.35, 'assists': 0.78, 'points': 1.13, 'shots': 3.2},
        {'name': 'Mika Zibanejad', 'goals': 0.40, 'assists': 0.52, 'points': 0.92, 'shots': 3.0},
        {'name': 'Vincent Trocheck', 'goals': 0.26, 'assists': 0.46, 'points': 0.72, 'shots': 2.3},
        {'name': 'Chris Kreider', 'goals': 0.42, 'assists': 0.30, 'points': 0.72, 'shots': 2.6},
    ],
}

# Sport configurations
SPORT_CONFIG = {
    'NBA': {
        'teams': list(NBA_TEAMS.keys()),
        'props': ['Points', 'Rebounds', 'Assists', 'PRA'],
        'stat_map': {
            'Points': 'ppg',
            'Rebounds': 'rpg',
            'Assists': 'apg',
            'PRA': ['ppg', 'rpg', 'apg']
        }
    },
    'NFL': {
        'teams': list(NFL_TEAMS.keys()),
        'props': ['Pass Yards', 'Pass TDs', 'Rush Yards', 'Receptions', 'Rec Yards'],
        'stat_map': {
            'Pass Yards': 'pass_yds',
            'Pass TDs': 'pass_td',
            'Rush Yards': 'rush_yds',
            'Receptions': 'rec',
            'Rec Yards': 'rec_yds'
        }
    },
    'MLB': {
        'teams': list(MLB_TEAMS.keys()),
        'props': ['Hits', 'Home Runs', 'RBIs'],
        'stat_map': {
            'Hits': 'hits',
            'Home Runs': 'hr',
            'RBIs': 'rbi'
        }
    },
    'NHL': {
        'teams': list(NHL_TEAMS.keys()),
        'props': ['Goals', 'Assists', 'Points', 'Shots'],
        'stat_map': {
            'Goals': 'goals',
            'Assists': 'assists',
            'Points': 'points',
            'Shots': 'shots'
        }
    }
}


def get_teams(sport: str):
    """Get teams for a sport."""
    if sport == 'NBA':
        return list(NBA_TEAMS.keys())
    elif sport == 'NFL':
        return list(NFL_TEAMS.keys())
    elif sport == 'MLB':
        return list(MLB_TEAMS.keys())
    elif sport == 'NHL':
        return list(NHL_TEAMS.keys())
    return []


def get_players(sport: str, team: str):
    """Get players for a team."""
    if sport == 'NBA':
        return NBA_TEAMS.get(team, [])
    elif sport == 'NFL':
        return NFL_TEAMS.get(team, [])
    elif sport == 'MLB':
        return MLB_TEAMS.get(team, [])
    elif sport == 'NHL':
        return NHL_TEAMS.get(team, [])
    return []


# Try to import NBA live data when available
try:
    from nba_api.stats.static import players as nba_players
    from nba_api.stats.endpoints import LeagueLeaders
    
    def get_nba_live_stats():
        """Get live NBA stats from nba_api."""
        try:
            leaders = LeagueLeaders(
                season='2024-25',
                season_type_all_star='Regular Season',
                stat_category_abbreviation='PTS'
            )
            return leaders.get_data_frames()[0]
        except:
            return None
            
    NBA_LIVE_AVAILABLE = True
except ImportError:
    NBA_LIVE_AVAILABLE = False
    
    def get_nba_live_stats():
        return None
