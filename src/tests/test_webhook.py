import requests
import os
import stripe
from dotenv import load_dotenv
import sys
import json

load_dotenv()

def test_webhook(event_id):
    """Test the Stripe webhook endpoint with a test event"""
    url = os.getenv('E8SCRIPTS_URL', 'http://localhost:5000')
    
    # Use test key
    stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')
    
    try:
        # Try to get the event first
        event = stripe.Event.retrieve(event_id)
        print(f"\nFound event: {event_id}")
        event_data = event
    except Exception as e:
        try:
            # If not an event, try as a checkout session
            session = stripe.checkout.Session.retrieve(event_id)
            print(f"\nFound checkout session: {event_id}")
            event_data = {
                'id': f'evt_test_{event_id[-8:]}',
                'type': 'checkout.session.completed',
                'data': {
                    'object': session
                }
            }
        except Exception as e2:
            print(f"\nError retrieving event/session: {str(e2)}")
            return False
    
    # Add test mode header
    headers = {
        'Content-Type': 'application/json',
        'X-Test-Mode': 'true',
        'Stripe-Signature': os.getenv('STRIPE_TEST_WEBHOOK_SECRET', '')
    }
    
    print("\nSending webhook request...")
    print(f"Event data: {json.dumps(event_data, indent=2)}")
    
    # Send webhook
    response = requests.post(
        f"{url}/billing/webhook",
        json=event_data,
        headers=headers
    )
    
    print(f"\nWebhook Response Status: {response.status_code}")
    print(f"Webhook Response: {response.json()}")
    
    return response.status_code == 200

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.tests.test_webhook <event_id_or_session_id>")
        sys.exit(1)
        
    event_id = sys.argv[1]
    if test_webhook(event_id):
        print("\nWebhook test successful!")
        print("You should receive a welcome email with login credentials.")
    else:
        print("\nWebhook test failed. Check the logs for more details.") 