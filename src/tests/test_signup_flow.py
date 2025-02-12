import requests
import json
import time
from datetime import datetime
from database import Database
import os
import base64

def test_signup_flow():
    # 1. Simulate E8solutions signup
    print("\n1. Testing signup from E8solutions...")
    signup_data = {
        'email': 'test@example.com',
        'priceId': os.getenv('STRIPE_TEST_PRICE_ID'),
        'source': 'e8solutions',
        'isTest': True
    }
    
    response = requests.post(
        'http://localhost:5000/subscribe/city-tagger',
        json=signup_data
    )
    print(f"Signup Response: {response.status_code}")
    session_data = response.json()
    print(session_data)
    
    if 'sessionId' not in session_data:
        print("Failed to get session ID")
        return
    
    # 2. Simulate Stripe webhook for successful subscription
    print("\n2. Simulating Stripe webhook for successful subscription...")
    session_id = session_data['sessionId']
    subscription_id = f"sub_test_{session_id[-8:]}"  # Generate unique subscription ID
    customer_id = f"cus_test_{session_id[-8:]}"  # Generate unique customer ID
    
    stripe_data = {
        'id': f"evt_test_{session_id[-8:]}",
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'id': session_id,
                'customer_email': signup_data['email'],
                'customer': customer_id,
                'subscription': subscription_id,
                'metadata': {
                    'isTest': True
                }
            }
        }
    }
    
    response = requests.post(
        'http://localhost:5000/billing/webhook',
        json=stripe_data,
        headers={
            'Stripe-Signature': 'test_signature',
            'X-Test-Mode': 'true'
        }
    )
    print(f"Stripe Webhook Response: {response.status_code}")
    print(response.json())
    
    # 3. Wait for welcome email (in real scenario) and simulate first login
    print("\n3. At this point, user would receive welcome email with temp password")
    time.sleep(2)
    
    # 4. Set up Follow Up Boss API key
    print("\n4. Setting up Follow Up Boss API key...")
    # Get the user and subscription
    user = Database.get_user_by_email(signup_data['email'])
    if user:
        subscription_data = Database.get_user_subscription(user.id)
        if subscription_data.data:
            subscription = subscription_data.data[0]
            Database.update_followupboss_api_key(subscription['id'], os.getenv('FOLLOWUPBOSS_API_KEY'))
            print("API key set successfully")
    
    # 5. Test Follow Up Boss webhook with a new lead
    print("\n5. Testing Follow Up Boss webhook with new lead...")
    test_lead_id = f"test_lead_{session_id[-8:]}"  # Use session ID to make unique test lead ID
    fub_data = {
        'eventId': f'evt_{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'event': 'peopleCreated',
        'resourceIds': [test_lead_id],
        'uri': f'/v1/people/{test_lead_id}',
        'system': 'city_tagger',
        'version': '1.0',
        'payload': {
            'id': test_lead_id,
            'source': 'Zillow',
            'sourceData': {
                'property': {
                    'street': '123 Main Street',
                    'city': 'Greeley',  # Using a city we know is in our list
                    'state': 'CO',
                    'code': '80631'
                }
            },
            'notes': [
                {
                    'message': 'New Zillow showing request for 123 Main Street, Greeley, CO 80631'
                }
            ]
        }
    }
    
    # Create base64 encoded auth header
    auth_string = f"{os.getenv('FOLLOWUPBOSS_API_KEY')}:"
    auth_bytes = auth_string.encode('ascii')
    base64_bytes = base64.b64encode(auth_bytes)
    base64_string = base64_bytes.decode('ascii')
    
    response = requests.post(
        'http://localhost:5000/webhook/followupboss',  # Updated endpoint
        json=fub_data,
        headers={
            'Authorization': f'Basic {base64_string}',
            'Content-Type': 'application/json',
            'X-Test-Mode': 'true'
        }
    )
    print(f"Follow Up Boss Webhook Response: {response.status_code}")
    print(response.json())
    
    # 6. Wait for execution and check history
    print("\n6. Waiting for execution to complete...")
    time.sleep(5)  # Give it time to process
    
    if user:
        subscription_data = Database.get_user_subscription(user.id)
        if subscription_data.data:
            subscription = subscription_data.data[0]
            executions = Database.get_subscription_executions(subscription['id'])
            if executions.data:
                print("\nExecution History:")
                for execution in executions.data:
                    print(f"Status: {execution['status']}")
                    print(f"Leads Processed: {execution['leads_processed']}")
                    print(f"Cities Tagged: {execution['cities_tagged']}")
                    if execution['error_message']:
                        print(f"Error: {execution['error_message']}")
    
    print("\nTest complete! Check the Flask server logs for more details.")

if __name__ == '__main__':
    test_signup_flow() 