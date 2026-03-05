"""
BetBrain AI - Email Capture API Endpoint
Vercel Serverless Function

Usage: POST /api/email-capture
Body: {"email": "user@example.com"}
Response: {"success": true, "redirect": "https://t.me/betbrainaiwinner"}
"""

import json
import os
import requests
from datetime import datetime
from pathlib import Path

def handler(request):
    """Vercel serverless function handler."""
    
    # Only allow POST
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        body = json.loads(request.body) if request.body else {}
        email = body.get('email')
        
        if not email or '@' not in email:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid email'})
            }
        
        # Save to JSON file (in repo - gets committed)
        data_dir = Path(__file__).parent.parent / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        emails_file = data_dir / 'waitlist_emails.json'
        
        # Load existing emails
        if emails_file.exists():
            with open(emails_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'emails': [], 'total': 0}
        
        # Add new email
        entry = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'source': 'landing-page'
        }
        
        data['emails'].append(entry)
        data['total'] = len(data['emails'])
        
        # Save back
        with open(emails_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Send Telegram notification
        try:
            send_telegram_notification(email)
        except Exception as e:
            print(f"Telegram notification failed: {e}")
        
        # Return success with redirect URL
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'redirect': 'https://t.me/betbrainaiwinner'
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def send_telegram_notification(email):
    """Send email to Telegram bot owner."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = '6471395025'  # Personal chat
    
    if not token:
        return
    
    message = f"""📧 <b>New Waitlist Signup!</b>

Email: <code>{email}</code>
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: Landing Page
Total: Check data/waitlist_emails.json
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    requests.post(url, json=data, timeout=5)

# Export handler for Vercel
main = handler
