#!/usr/bin/env python3
"""Add real-time player props cron job (30 minute updates)"""

import json
import os
from datetime import datetime, timedelta

# Read existing jobs
cron_path = os.path.expanduser('~/.openclaw/cron/jobs.json')
with open(cron_path, 'r') as f:
    data = json.load(f)

# Create new job
new_job = {
    "id": f"player-props-realtime-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    "agentId": "main",
    "sessionKey": "agent:main:main",
    "name": "player-props-realtime",
    "description": "Real-time player props from sportsbooks (30min updates)",
    "enabled": True,
    "createdAtMs": int(datetime.now().timestamp() * 1000),
    "updatedAtMs": int(datetime.now().timestamp() * 1000),
    "schedule": {
        "everyMs": 1800000,  # 30 minutes
        "kind": "every",
        "anchorMs": int(datetime.now().timestamp() * 1000)
    },
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
        "kind": "systemEvent",
        "text": "cd /Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api && python3 player_props_scraper.py && cd /Users/djryan/git/guiltyfalcon/ai-portfolio && git add sports-betting-ai/api/player_props_cache.json && git commit -m 'Auto-update player props (30min)' && git push"
    },
    "state": {
        "nextRunAtMs": int((datetime.now() + timedelta(minutes=30)).timestamp() * 1000),
        "lastRunAtMs": None,
        "lastStatus": None,
        "lastDurationMs": None,
        "lastRunStatus": None,
        "lastDeliveryStatus": None,
        "consecutiveErrors": 0
    }
}

# Add to jobs
data['jobs'].append(new_job)

# Write back
with open(cron_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"✅ Added cron job: {new_job['name']}")
print(f"   Runs every 30 minutes")
print(f"   Next run: {datetime.fromtimestamp(new_job['state']['nextRunAtMs']/1000)}")
