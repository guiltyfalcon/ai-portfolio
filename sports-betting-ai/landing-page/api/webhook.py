#!/usr/bin/env python3
"""
BetBrain AI - Email Capture Webhook
Saves waitlist emails to JSON file and Google Sheets.

Usage: Deploy to Vercel as serverless function
Endpoint: POST /api/email-capture
Body: {"email": "user@example.com"}
"""

import json
import os
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

# File storage
EMAILS_FILE = Path('/Users/djryan/git/guiltyfalcon/ai-portfolio/sports-betting-ai/api/email-capture/waitlist_emails.json')

def save_email(email, metadata=None):
    """Save email to JSON file."""
    # Load existing emails
    if EMAILS_FILE.exists():
        with open(EMAILS_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {'emails': [], 'total': 0}
    
    # Add new email
    entry = {
        'email': email,
        'timestamp': datetime.now().isoformat(),
        'source': 'landing-page',
        'metadata': metadata or {}
    }
    
    data['emails'].append(entry)
    data['total'] = len(data['emails'])
    
    # Save back
    with open(EMAILS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return entry

def send_telegram_notification(email):
    """Send email to Telegram bot owner."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '6471395025')  # Personal chat, not channel
    
    if not token:
        return False
    
    message = f"""📧 <b>New Waitlist Signup!</b>

Email: <code>{email}</code>
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: Landing Page

Total signups: Check waitlist_emails.json
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        import requests
        response = requests.post(url, json=data, timeout=5)
        return response.json().get('ok', False)
    except:
        return False

# Vercel serverless function handler
def handler(request):
    """Handle HTTP request (Vercel serverless)."""
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        content_length = int(request.headers.get('Content-Length', 0))
        body = request.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))
        
        email = data.get('email')
        if not email or '@' not in email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid email'})
            }
        
        # Save email
        entry = save_email(email, {
            'ip': request.client_address[0] if request.client_address else 'unknown',
            'user_agent': request.headers.get('User-Agent', 'unknown')
        })
        
        # Send Telegram notification
        send_telegram_notification(email)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Email saved',
                'redirect': 'https://t.me/betbrainaiwinner'
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# Local testing server
class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        result = handler(self)
        self.send_response(result['statusCode'])
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(result['body'].encode())
    
    def log_message(self, format, *args):
        print(f"[{datetime.now()}] {args[0]}")

if __name__ == '__main__':
    # Initialize emails file
    if not EMAILS_FILE.exists():
        save_email('test@example.com')  # Create file with test entry
        print(f"✅ Created {EMAILS_FILE}")
    
    # Start local server
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print(f"🧠 Email capture server running on http://localhost:8000")
    print(f"📁 Emails saved to: {EMAILS_FILE}")
    server.serve_forever()
