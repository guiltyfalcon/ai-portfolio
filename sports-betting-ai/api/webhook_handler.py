#!/usr/bin/env python3
"""
Stripe Webhook Handler for Sports Betting AI
Receives payment notifications and activates premium accounts

Usage:
1. Deploy this as a serverless function (Vercel, Netlify, Railway)
2. Set STRIPE_WEBHOOK_SECRET in environment
3. Point Stripe webhook to: https://your-domain.com/api/webhook
"""

import os
import json
import hmac
import hashlib
from datetime import datetime

def verify_stripe_signature(payload, sig_header, secret):
    """Verify webhook is actually from Stripe"""
    try:
        # Stripe format: t=timestamp,v1=signature
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
        
        # Reconstruct signed payload
        signed_payload = f"{timestamp}.{payload}"
        expected = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

def handle_checkout_completed(session):
    """Process successful payment"""
    customer_email = session.get('customer_details', {}).get('email')
    customer_id = session.get('customer')
    amount = session.get('amount_total', 0) / 100  # Convert from cents
    
    # Log the activation
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'email': customer_email,
        'customer_id': customer_id,
        'amount': amount,
        'status': 'activated'
    }
    
    # Write to local file (in production, use database)
    user_flag_file = os.path.expanduser(f"~/.openclaw/sports_bet_users/{customer_id}.txt")
    os.makedirs(os.path.dirname(user_flag_file), exist_ok=True)
    
    with open(user_flag_file, 'w') as f:
        f.write(json.dumps(log_entry))
    
    print(f"✅ Premium activated for {customer_email}")
    return True

def webhook_handler(event, context=None):
    """Main webhook entry point"""
    
    # For Vercel/Netlify serverless
    if isinstance(event, dict):
        method = event.get('httpMethod', 'POST')
        headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
        body = event.get('body', '')
    else:
        # For local testing
        method = 'POST'
        headers = {}
        body = event
    
    # Only accept POST requests
    if method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    # Verify signature (optional in dev, required in prod)
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    sig_header = headers.get('stripe-signature', '')
    
    if webhook_secret and sig_header:
        if not verify_stripe_signature(body, sig_header, webhook_secret):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid signature'})
            }
    
    try:
        payload = json.loads(body)
        event_type = payload.get('type')
        
        print(f"📩 Webhook received: {event_type}")
        
        if event_type == 'checkout.session.completed':
            session = payload.get('data', {}).get('object', {})
            handle_checkout_completed(session)
            
        elif event_type == 'checkout.session.expired':
            print("⏰ Checkout expired")
            
        elif event_type == 'charge.refunded':
            print("💰 Refund processed")
            # Could deactivate premium here
            
        else:
            print(f"ℹ️  Unhandled event type: {event_type}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'received': True})
        }
        
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

# For local Flask/FastAPI server
if __name__ == '__main__':
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        event = {
            'httpMethod': request.method,
            'headers': dict(request.headers),
            'body': request.get_data(as_text=True)
        }
        result = webhook_handler(event)
        return result.get('body'), result.get('statusCode')
    
    print("🚀 Webhook server running on http://localhost:5000")
    print("Test with: curl -X POST http://localhost:5000/webhook -d '{test}'")
    app.run(port=5000)
