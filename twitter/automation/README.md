# Twitter Automation Workflow

## Overview
Automated Twitter growth and engagement for @holikidTV (BetBrain AI).

## Scheduled Tasks

| Time (ET) | Task | Sub-agent | Reminder |
|-----------|------|-----------|----------|
| 9:00 AM | Post daily NBA picks thread | ✅ | `twitter-morning-picks` |
| 2:00 PM | Follow 5-10 accounts + engage | ✅ | `twitter-afternoon-growth` |
| 6:00 PM | Retweet 2-3 betting news items | ✅ | `twitter-evening-engagement` |

## How It Works

1. **Cron jobs** trigger reminders at scheduled times
2. **Reminders** prompt the main agent to spawn sub-agents
3. **Sub-agents** execute browser automation tasks
4. **Activity log** tracks all actions for review

## Sub-agent Delegation

**Main agent should NEVER execute Twitter tasks directly.** Always spawn sub-agents:

```
sessions_spawn(
  runtime="subagent",
  task="Execute Twitter follows for accounts: [list]",
  mode="run"
)
```

## Files

- `twitter_engagement.py` - Main automation script
- `activity.log` - Execution history
- `target_accounts.md` - Accounts to follow/engage with

## Manual Execution

```bash
cd /Users/djryan/git/guiltyfalcon/ai-portfolio/twitter/automation
python3 twitter_engagement.py --follows
python3 twitter_engagement.py --retweets
python3 twitter_engagement.py --post-picks
```

## Monitoring

Check activity log: `tail -f activity.log`

Review Twitter analytics weekly for engagement metrics.
