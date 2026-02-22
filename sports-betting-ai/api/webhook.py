#!/usr/bin/env python3
"""
Stripe Webhook Handler - Vercel Serverless Function
Receives subscription events and manages premium access
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
        print(f"Verify error: {e}")
        return False

def save_subscription(customer_id, data):
    """Save subscription to file"""
    user_file = f".subscriptions/{customer_id}.json"
    os.makedirs(os.path.dirname(user_file), exist_ok=True)
    
    with open(user_file, 'w') as f:
        json.dump(data, f)
    
    print(f"✅ Saved: {customer_id}")

def handler(request):
    """Vercel serverless handler"""
    
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    sig_header = request.headers.get('stripe-signature', '')
    body = request.body.decode('utf-8') if hasattr(request.body, 'decode') else str(request.body)
    
    # Verify signature
    if webhook_secret and sig_header:
        if not verify_stripe_signature(body, sig_header, webhook_secret):
            return {"statusCode": 401, "body": json.dumps({"error": "Invalid signature"})}
    
    try:
        payload = json.loads(body)
        event_type = payload.get('type')
        data = payload.get('data', {}).get('object', {})
        
        print(f"📩 {event_type}")
        
        if event_type == 'checkout.session.completed':
            customer_id = data.get('customer')
            subscription_data = {
                'customer_id': customer_id,
                'email': data.get('customer_details', {}).get('email'),
                'status': 'active',
                'started_at': datetime.now().isoformat(),
                'last_payment': datetime.now().isoformat(),
                'amount': 5.00,
                'is_cancelled': False
            }
            save_subscription(customer_id, subscription_data)
            
        elif event_type == 'invoice.paid':
            customer_id = data.get('customer')
            print(f"💳 Monthly payment: {customer_id}")
            
        elif event_type == 'customer.subscription.deleted':
            customer_id = data.get('customer')
            user_file = f".subscriptions/{customer_id}.json"
            if os.path.exists(user_file):
                with open(user_file, 'r') as f:
                    subscription_data = json.load(f)
                subscription_data['status'] = 'cancelled'
                subscription_data['is_cancelled'] = True
                subscription_data['cancelled_at'] = datetime.now().isoformat()
                save_subscription(customer_id, subscription_data)
                print(f"❌ Cancelled: {customer_id}")
        
        return {"statusCode": 200, "body": json.dumps({"received": True})}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}

# For testing locally
if __name__ == "__main__":
    print("Stripe Webhook Handler")
    print("Set STRIPE_WEBHOOK_SECRET environment variable to test")
