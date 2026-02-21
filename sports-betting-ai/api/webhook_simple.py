#!/usr/bin/env python3
"""
Simple webhook server with built-in tunnel info
Run this, then use ngrok.com to get tunnel
"""

import os
import json
import hmac
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# In-memory storage
USERS_FILE = os.path.expanduser("~/.openclaw/sports_bet_webhook_users.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            payload = json.loads(body)
            event_type = payload.get('type')
            data = payload.get('data', {}).get('object', {})
            
            print(f"📩 Webhook received: {event_type}")
            
            if event_type == 'checkout.session.completed':
                customer_id = data.get('customer')
                email = data.get('customer_details', {}).get('email')
                users = load_users()
                users[customer_id] = {
                    'status': 'active',
                    'email': email,
                    'started_at': datetime.now().isoformat(),
                    'amount': data.get('amount_total', 0) / 100
                }
                save_users(users)
                print(f"✅ ACTIVATED: {email}")
                
            elif event_type == 'customer.subscription.deleted':
                customer_id = data.get('customer')
                users = load_users()
                if customer_id in users:
                    users[customer_id]['status'] = 'cancelled'
                    users[customer_id]['cancelled_at'] = datetime.now().isoformat()
                    save_users(users)
                print(f"❌ CANCELLED: {customer_id}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"received": true}')
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        users = load_users()
        self.wfile.write(json.dumps({
            'status': 'running',
            'active_users': len([u for u in users.values() if u.get('status') == 'active'])
        }).encode())

if __name__ == '__main__':
    PORT = 9999  # Match ngrok port
    
    print("="*60)
    print("🎯 SPORTS BETTING WEBHOOK SERVER")
    print("="*60)
    print(f"Local endpoint: http://localhost:{PORT}/webhook")
    print(f"Health check:   http://localhost:{PORT}")
    print("")
    print("🔑 ACTIVATED USERS:")
    users = load_users()
    if users:
        for uid, data in users.items():
            if data.get('status') == 'active':
                print(f"  ✓ {data.get('email', uid)[:30]}")
    else:
        print("  (No users yet)")
    print("")
    print("⚠️  NEED PUBLIC URL?")
    print("   Option 1: ngrok http 8765")
    print("   Option 2: cloudflared tunnel --url http://localhost:8765")
    print("   Option 3: Go to ngrok.com, download, run: ./ngrok http 8765")
    print("")
    print("📋 STRIPE SETUP:")
    print("   1. Add webhook endpoint to your ngrok URL + /webhook")
    print("   2. Events: checkout.session.completed")
    print("   3. Copy signing secret, set as STRIPE_WEBHOOK_SECRET")
    print("="*60)
    print("")
    
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
