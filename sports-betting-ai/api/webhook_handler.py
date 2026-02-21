#!/usr/bin/env python3
"""
Stripe Webhook Handler for Sports Betting AI - SUBSCRIPTION MODEL
Receives subscription events and manages premium access

Events to handle:
- checkout.session.completed (initial subscription)
- invoice.paid (monthly renewal)
- invoice.payment_failed (payment issues)
- customer.subscription.deleted (cancelled)
"""

import os
import json
import hmac
import hashlib
from datetime import datetime

def verify_stripe_signature(payload, sig_header, secret):
    """Verify webhook is actually from Stripe"""
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
        print(f"Signature verification error: {e}")
        return False

def get_user_file_path(customer_id):
    """Get path to user subscription file"""
    return os.path.expanduser(f"~/.openclaw/sports_bet_users/{customer_id}.json")

def save_subscription(customer_id, data):
    """Save subscription data to file"""
    user_file = get_user_file_path(customer_id)
    os.makedirs(os.path.dirname(user_file), exist_ok=True)
    
    with open(user_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Subscription saved for {customer_id}")

def load_subscription(customer_id):
    """Load subscription data"""
    user_file = get_user_file_path(customer_id)
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            return json.load(f)
    return None

def handle_checkout_completed(session):
    """New subscription started"""
    customer_email = session.get('customer_details', {}).get('email')
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')  # If you used Stripe Subscription mode
    
    subscription_data = {
        'customer_id': customer_id,
        'email': customer_email,
        'subscription_id': subscription_id,
        'status': 'active',
        'started_at': datetime.now().isoformat(),
        'last_payment': datetime.now().isoformat(),
        'next_payment': None,  # Will be updated by invoice.paid
        'amount_paid': 5.00,
        'is_cancelled': False,
        'cancel_at_period_end': False
    }
    
    save_subscription(customer_id, subscription_data)
    print(f"✅ New subscription: {customer_email} - $5/month")
    
    # Could send Telegram notification here
    return True

def handle_invoice_paid(invoice):
    """Monthly payment succeeded"""
    customer_id = invoice.get('customer')
    subscription = load_subscription(customer_id)
    
    if subscription:
        subscription['status'] = 'active'
        subscription['last_payment'] = datetime.now().isoformat()
        subscription['period_end'] = invoice.get('period_end')  # Unix timestamp
        subscription['amount_paid'] = invoice.get('amount_paid', 0) / 100
        
        save_subscription(customer_id, subscription)
        print(f"💳 Monthly payment received: {subscription.get('email')} - ${subscription['amount_paid']}")
    else:
        print(f"⚠️ Invoice paid but no customer found: {customer_id}")

def handle_payment_failed(invoice):
    """Payment failed - notify but don't deactivate immediately"""
    customer_id = invoice.get('customer')
    subscription = load_subscription(customer_id)
    
    if subscription:
        subscription['last_payment_failed'] = datetime.now().isoformat()
        subscription['next_payment_attempt'] = invoice.get('next_payment_attempt')
        save_subscription(customer_id, subscription)
        print(f"⚠️ Payment failed: {subscription.get('email')}")

def handle_subscription_cancelled(subscription_obj):
    """Subscription cancelled"""
    customer_id = subscription_obj.get('customer')
    subscription = load_subscription(customer_id)
    
    if subscription:
        subscription['is_cancelled'] = True
        subscription['cancelled_at'] = datetime.now().isoformat()
        subscription['status'] = 'cancelled'
        
        # Keep premium until period ends
        subscription['premium_until'] = subscription_obj.get('current_period_end')
        
        save_subscription(customer_id, subscription)
        print(f"❌ Subscription cancelled: {subscription.get('email')}")

def webhook_handler(event, context=None):
    """Main webhook entry point"""
    
    # For Vercel/Netlify serverless
    if isinstance(event, dict):
        method = event.get('httpMethod', 'POST')
        headers = {k.lower(): v for k, v in event.get('headers', {}).items()}
        body = event.get('body', '')
    else:
        method = 'POST'
        headers = {}
        body = event
    
    if method != 'POST':
        return {'statusCode': 405, 'body': json.dumps({'error': 'Method not allowed'})}
    
    # Verify signature
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    sig_header = headers.get('stripe-signature', '')
    
    if webhook_secret and sig_header:
        if not verify_stripe_signature(body, sig_header, webhook_secret):
            return {'statusCode': 401, 'body': json.dumps({'error': 'Invalid signature'})}
    
    try:
        payload = json.loads(body)
        event_type = payload.get('type')
        
        print(f"📩 Webhook: {event_type}")
        
        if event_type == 'checkout.session.completed':
            session = payload.get('data', {}).get('object', {})
            handle_checkout_completed(session)
            
        elif event_type == 'invoice.paid':
            invoice = payload.get('data', {}).get('object', {})
            handle_invoice_paid(invoice)
            
        elif event_type == 'invoice.payment_failed':
            invoice = payload.get('data', {}).get('object', {})
            handle_payment_failed(invoice)
            
        elif event_type == 'customer.subscription.deleted':
            subscription = payload.get('data', {}).get('object', {})
            handle_subscription_cancelled(subscription)
            
        elif event_type == 'customer.subscription.updated':
            subscription = payload.get('data', {}).get('object', {})
            if subscription.get('cancel_at_period_end'):
                print(f"⏰ Subscription will cancel at period end: {subscription.get('customer')}")
        
        else:
            print(f"ℹ️  Ignoring event: {event_type}")
        
        return {'statusCode': 200, 'body': json.dumps({'received': True})}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'statusCode': 400, 'body': json.dumps({'error': str(e)})}

# For local Flask server
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
    
    print("🚀 Webhook server: http://localhost:5000")
    print("Test: curl -X POST http://localhost:5000/webhook -d '{test}'")
    app.run(port=5000)
