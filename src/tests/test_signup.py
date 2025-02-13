import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_subscription():
    """Test creating a subscription checkout session"""
    url = os.getenv('E8SCRIPTS_URL', 'http://localhost:5000')
    
    data = {
        "email": "test@example.com",
        "priceId": os.getenv('STRIPE_TEST_PRICE_ID'),
        "isTest": True,
        "source": "test"
    }
    
    response = requests.post(f"{url}/subscribe/city-tagger", json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    if response.status_code == 200:
        session_id = response.json().get('sessionId')
        print(f"\nCheckout URL: https://checkout.stripe.com/c/pay/{session_id}")
        return session_id
    return None

if __name__ == "__main__":
    session_id = test_subscription()
    if session_id:
        print("\nSuccess! Use the checkout URL above to complete the test subscription.")
        print("After payment, you should receive a welcome email with login credentials.") 