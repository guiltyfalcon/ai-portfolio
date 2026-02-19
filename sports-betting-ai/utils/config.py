# Configuration and utilities for Sports Betting AI

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
THEODDS_API_KEY = os.getenv('THEODDS_API_KEY', '8fcaab13355be4098fc79f7dbce9821b')

# Model Settings
MODEL_CONFIG = {
    'nba': {
        'base_elo': 1500,
        'home_advantage': 65,
        'k_factor': 20
    },
    'nfl': {
        'base_elo': 1500,
        'home_advantage': 45,
        'k_factor': 15
    },
    'mlb': {
        'base_elo': 1500,
        'home_advantage': 35,
        'k_factor': 8
    },
    'nhl': {
        'base_elo': 1500,
        'home_advantage': 40,
        'k_factor': 12
    }
}

# Betting Settings
VALUE_THRESHOLD = 0.05  # 5% edge minimum
MAX_BET_SIZE = 100  # Units

# Sports mapping
SPORTS = {
    'nba': 'Basketball - NBA',
    'nfl': 'Football - NFL',
    'mlb': 'Baseball - MLB',
    'nhl': 'Hockey - NHL'
}
