import requests
import os
import stripe
from dotenv import load_dotenv

load_dotenv()

def test_webhook(session_id):
    """Test the Stripe webhook endpoint with a test event"""
    url = os.getenv('E8SCRIPTS_URL', 'http://localhost:5000')
    
    # Use test key
    stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')
    
    # Get the session data
    session = stripe.checkout.Session.retrieve(session_id)
    
    # Create a test event
    event_data = {
        'id': 'evt_test_webhook',
        'type': 'checkout.session.completed',
        'data': {
            'object': session
        }
    }
    
    # Add test mode header
    headers = {
        'Content-Type': 'application/json',
        'X-Test-Mode': 'true'
    }
    
    # Send webhook
    response = requests.post(
        f"{url}/billing/webhook",
        json=event_data,
        headers=headers
    )
    
    print(f"Webhook Response Status: {response.status_code}")
    print(f"Webhook Response: {response.json()}")
    
    return response.status_code == 200

if __name__ == "__main__":
    session_id = input("Enter the Stripe checkout session ID: ")
    if test_webhook(session_id):
        print("\nWebhook test successful!")
        print("You should receive a welcome email with login credentials.") 