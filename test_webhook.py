#!/usr/bin/env python3
"""
Test script for PayPal webhook integration
Use this to test your webhook endpoint with ngrok
"""

import requests
import json
from datetime import datetime

def test_webhook_endpoint(webhook_url):
    """Test the webhook endpoint with a sample PAYMENT.CAPTURE.COMPLETED event"""
    
    # Sample webhook payload for PAYMENT.CAPTURE.COMPLETED
    webhook_payload = {
        "id": "WH-2WR32451HC0233532-67976317FL4543714",
        "event_version": "1.0",
        "create_time": "2025-12-08T18:41:29.032Z",
        "resource_type": "capture",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "summary": "Payment completed",
        "resource": {
            "id": "5O190127TN364715T",
            "status": "COMPLETED",
            "amount": {
                "currency_code": "USD",
                "value": "45.00"
            },
            "supplementary_data": {
                "related_ids": {
                    "order_id": "4HS123456789012345"
                }
            }
        },
        "links": []
    }
    
    # Sample headers (without real signature for testing)
    headers = {
        'Content-Type': 'application/json',
        'PAYPAL-TRANSMISSION-ID': 'test-transmission-id',
        'PAYPAL-CERT-ID': 'test-cert-id', 
        'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
        'PAYPAL-TRANSMISSION-SIG': 'test-signature',
        'PAYPAL-TRANSMISSION-TIME': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        response = requests.post(webhook_url, json=webhook_payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook endpoint is working!")
        else:
            print("❌ Webhook endpoint returned an error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to reach webhook endpoint: {e}")

def create_test_order_with_metadata():
    """
    Sample PayPal order creation with custom_id metadata
    This shows how your frontend should create orders
    """
    
    # Sample metadata for webhook
    booking_metadata = {
        "event_id": 1,
        "tickets": 2,
        "phone": "555-123-4567",
        "email": "test@example.com"
    }
    
    order_data = {
        "purchase_units": [{
            "amount": {
                "value": "45.00",
                "currency_code": "USD"
            },
            "custom_id": json.dumps(booking_metadata)
        }]
    }
    
    print("Sample PayPal order creation with metadata:")
    print(json.dumps(order_data, indent=2))
    
    return order_data

def main():
    print("PayPal Webhook Test Script")
    print("=" * 40)
    
    # Show sample order creation
    print("\n1. Sample PayPal Order with Metadata:")
    create_test_order_with_metadata()
    
    print("\n2. Testing Webhook Endpoint:")
    
    # Test with ngrok URL (update this to your actual ngrok URL)
    ngrok_url = input("Enter your ngrok webhook URL (e.g., https://abc123.ngrok-free.app/paypal/webhook): ").strip()
    
    if ngrok_url:
        test_webhook_endpoint(ngrok_url)
    else:
        print("No URL provided, skipping webhook test")
    
    print("\n3. Setup Instructions:")
    print("To test your webhook implementation:")
    print("1. Start your Flask app: python app.py")
    print("2. Start ngrok: ngrok http 5000")
    print("3. Copy the ngrok HTTPS URL")
    print("4. Run this test script with the webhook URL")
    print("5. Register the webhook URL in PayPal Sandbox")
    print("6. Perform a test transaction")

if __name__ == "__main__":
    main()