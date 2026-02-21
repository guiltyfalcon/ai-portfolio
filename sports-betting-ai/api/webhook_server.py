#!/usr/bin/env python3
"""
Simple webhook server - run locally, expose via ngrok
"""

import os
import json
import hmac
import hashlib
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# In-memory storage (resets on restart - use file for persistence)
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

def verify_signature(payload, sig_header, secret):
    """Verify Stripe signature"""
    try:
        elements = sig_header.split(',')
        sig_dict = {}
        for element in elements:
            if '=' in element:
                key, value = element.split('=', 1)
                sig_dict[key.strip()] = value.strip()
        
        timestamp = sig_dict.get('t')
        signature = sig_dict.get('v1')
        
        if not timestamp or not signature:
            return False
        
        signed_payload = f"{timestamp}.{payload}"
        expected = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        print(f"Verify error: {e}")
        return False

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def do_POST(self):
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        sig_header = self.headers.get('stripe-signature', '')
        
        # Verify signature
        if webhook_secret and sig_header:
            if not verify_signature(body, sig_header, webhook_secret):
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid signature"}')
                return
        
        try:
            payload = json.loads(body)
            event_type = payload.get('type')
            data = payload.get('data', {}).get('object', {})
            
            print(f"📩 Webhook: {event_type}")
            
            if event_type == 'checkout.session.completed':
                customer_id = data.get('customer')
                users = load_users()
                users[customer_id] = {
                    'status': 'active',
                    'email': data.get('customer_details', {}).get('email'),
                    'started_at': datetime.now().isoformat(),
                    'amount': data.get('amount_total', 0) / 100
                }
                save_users(users)
                print(f"✅ Activated: {customer_id}")
                
            elif event_type == 'customer.subscription.deleted':
                customer_id = data.get('customer')
                users = load_users()
                if customer_id in users:
                    users[customer_id]['status'] = 'cancelled'
                    users[customer_id]['cancelled_at'] = datetime.now().isoformat()
                    save_users(users)
                print(f"❌ Cancelled: {customer_id}")
            
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
        self.wfile.write(b'{"status": "Webhook server running"}')

if __name__ == '__main__':
    PORT = 8765  # Changed from 5000 to avoid conflicts
    print(f"🚀 Webhook server starting on port {PORT}")
    print(f"Health check: http://localhost:{PORT}")
    print(f"Webhook endpoint: http://localhost:{PORT}/webhook")
    print(f"\nTo expose publicly, run in another terminal:")
    print(f"  ngrok http {PORT}")
    print(f"\nThen use the ngrok URL in Stripe webhook settings\n")
    
    server = HTTPServer(('0.0.0.0', PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
