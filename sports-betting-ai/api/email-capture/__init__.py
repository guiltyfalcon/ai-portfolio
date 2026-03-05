"""
BetBrain AI - Email Capture API Endpoint
Vercel Serverless Function

Usage: POST /api/email-capture
Body: {"email": "user@example.com"}
Response: {"success": true, "redirect": "https://t.me/betbrainaiwinner"}
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Vercel serverless handler
def POST(request):
    """Handle POST request to save email."""
    
    # File storage path (Vercel ephemeral - use external storage in production)
    # For now, we'll use a JSON file that gets committed to Git
    EMAILS_FILE = Path(__file__).parent.parent / 'data' / 'waitlist_emails.json'
    
    try:
        # Parse request body
        body = request.json if hasattr(request, 'json') else json.loads(request.body)
        email = body.get('email')
        
        if not email or '@' not in email:
            return Response(
                json.dumps({'error': 'Invalid email'}),
                status=400,
                headers={'Content-Type': 'application/json'}
            )
        
        # Load existing emails
        if EMAILS_FILE.exists():
            with open(EMAILS_FILE, 'r') as f:
                data = json.load(f)
        else:
            data = {'emails': [], 'total': 0}
            # Ensure directory exists
            EMAILS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Add new email
        entry = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'source': 'landing-page'
        }
        
        data['emails'].append(entry)
        data['total'] = len(data['emails'])
        
        # Save back
        with open(EMAILS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Send Telegram notification (optional)
        try:
            send_telegram_notification(email)
        except:
            pass  # Don't fail if Telegram notification fails
        
        # Return success with redirect URL
        return Response(
            json.dumps({
                'success': True,
                'redirect': 'https://t.me/betbrainaiwinner'
            }),
            status=200,
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
    except Exception as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=500,
            headers={'Content-Type': 'application/json'}
        )

def send_telegram_notification(email):
    """Send email to Telegram bot owner."""
    import requests
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '6471395025')
    
    if not token:
        return
    
    message = f"""📧 <b>New Waitlist Signup!</b>

Email: <code>{email}</code>
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: Landing Page
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    requests.post(url, json=data, timeout=5)

# Simple Response class for compatibility
class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}
