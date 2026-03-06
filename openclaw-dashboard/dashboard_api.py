#!/usr/bin/env python3
"""
OpenClaw Monitoring Dashboard
Real-time view of all OpenClaw functions, subagents, cron jobs, and system health.

Usage: python3 openclaw_dashboard.py
Features:
- Live session/subagent monitoring
- Cron job status tracking
- Recent execution logs
- Error alerts
- System resource usage
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import os

class OpenClawDashboard:
    def __init__(self):
        self.workspace = Path('/Users/djryan')
        self.log_dir = self.workspace / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
    def get_subagent_status(self) -> Dict:
        """Get current subagent sessions."""
        try:
            result = subprocess.run(
                ['openclaw', 'subagents', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return {
                'status': 'active',
                'output': result.stdout,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_cron_status(self) -> Dict:
        """Get current cron jobs."""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            jobs = []
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('#'):
                    jobs.append(line)
            return {
                'total_jobs': len(jobs),
                'jobs': jobs,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Get recent log entries."""
        logs = []
        log_files = [
            '/tmp/betbrain-morning.log',
            '/tmp/betbrain-updates.log',
            '/tmp/betbrain-evening.log',
            '/tmp/betbrain-welcome.log',
            '/tmp/betbrain-digest.log',
            '/tmp/betbrain-weekly-props.log'
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        content = f.readlines()
                        logs.extend(content[-lines:])
                except:
                    pass
        
        return logs[-lines:] if logs else ['No logs found']
    
    def get_git_status(self) -> Dict:
        """Check git repository status."""
        try:
            os.chdir('/Users/djryan/git/guiltyfalcon/ai-portfolio')
            result = subprocess.run(
                ['git', 'status', '--short'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return {
                'clean': len(result.stdout.strip()) == 0,
                'changes': result.stdout.strip().split('\n') if result.stdout.strip() else [],
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_system_health(self) -> Dict:
        """Get basic system health metrics."""
        try:
            # Disk usage
            disk = subprocess.run(
                ['df', '-h', '/Users/djryan'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Memory usage
            memory = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'disk': disk.stdout,
                'memory': memory.stdout[:500],  # Truncate
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard."""
        subagents = self.get_subagent_status()
        cron = self.get_cron_status()
        logs = self.get_recent_logs(30)
        git = self.get_git_status()
        health = self.get_system_health()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>OpenClaw Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #333;
        }}
        .card h2 {{
            margin-top: 0;
            color: #667eea;
            font-size: 1.3em;
        }}
        .status-good {{ color: #4ade80; }}
        .status-warn {{ color: #fbbf24; }}
        .status-error {{ color: #f87171; }}
        pre {{
            background: #0a0a0a;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 0.85em;
            max-height: 300px;
            overflow-y: auto;
        }}
        .metric {{
            display: inline-block;
            background: #333;
            padding: 10px 20px;
            border-radius: 8px;
            margin: 5px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.85em;
        }}
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="header">
        <h1>🧠 OpenClaw Dashboard</h1>
        <p>BetBrain AI Automation Monitor</p>
        <p class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>📊 System Overview</h2>
            <div class="metric">
                <div class="metric-value">{cron.get('total_jobs', 0)}</div>
                <div>Cron Jobs</div>
            </div>
            <div class="metric">
                <div class="metric-value">{'✓' if git.get('clean') else '!'}</div>
                <div>Git Status</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🤖 Subagent Status</h2>
            <pre>{subagents.get('output', 'No active subagents')}</pre>
        </div>
        
        <div class="card">
            <h2>⏰ Active Cron Jobs</h2>
            <pre>{chr(10).join(cron.get('jobs', []))}</pre>
        </div>
        
        <div class="card">
            <h2>📝 Recent Logs</h2>
            <pre>{chr(10).join(logs)}</pre>
        </div>
        
        <div class="card">
            <h2>💾 System Health</h2>
            <pre>{health.get('disk', 'N/A')}</pre>
        </div>
        
        <div class="card">
            <h2>🔧 Git Repository</h2>
            <p class="{'status-good' if git.get('clean') else 'status-warn'}">
                {'✅ Clean' if git.get('clean') else '⚠️ Uncommitted Changes'}
            </p>
            <pre>{chr(10).join(git.get('changes', []))}</pre>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_dashboard(self):
        """Save dashboard to file."""
        html = self.generate_html_dashboard()
        output_path = self.workspace / 'openclaw_dashboard.html'
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"✅ Dashboard saved to: {output_path}")
        return output_path
    
    def print_console_dashboard(self):
        """Print dashboard to console."""
        print("\n" + "="*70)
        print("🧠 OPENCLAW DASHBOARD".center(70))
        print("="*70)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Cron jobs
        cron = self.get_cron_status()
        print(f"\n⏰ CRON JOBS: {cron.get('total_jobs', 0)} active")
        for job in cron.get('jobs', [])[:5]:
            print(f"  • {job[:60]}...")
        
        # Recent logs
        print(f"\n📝 RECENT LOGS:")
        logs = self.get_recent_logs(10)
        for log in logs:
            print(f"  {log.strip()}")
        
        # Git status
        git = self.get_git_status()
        print(f"\n🔧 GIT STATUS: {'✅ Clean' if git.get('clean') else '⚠️ Changes pending'}")
        
        print("\n" + "="*70)
        print("💡 Tip: Run 'python3 openclaw_dashboard.py --html' for web view")
        print("="*70 + "\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='OpenClaw Dashboard')
    parser.add_argument('--html', action='store_true', help='Generate HTML dashboard')
    args = parser.parse_args()
    
    dashboard = OpenClawDashboard()
    
    if args.html:
        path = dashboard.save_dashboard()
        print(f"\n🌐 Open in browser: file://{path}")
    else:
        dashboard.print_console_dashboard()

if __name__ == '__main__':
    main()
