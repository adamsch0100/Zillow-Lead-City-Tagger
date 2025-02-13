import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_subscription():
    """Test creating a subscription checkout session"""
    # Use localhost for testing, but default to e8scripts.io in production
    url = os.getenv('E8SCRIPTS_URL', 'https://e8scripts.io')
    
    data = {
        "email": "test@example.com",
        "priceId": os.getenv('STRIPE_TEST_PRICE_ID'),
        "isTest": True,
        "source": "test"
    }
    
    print(f"Sending request to {url}/subscribe/city-tagger")
    print(f"Request data: {data}")
    
    response = requests.post(f"{url}/subscribe/city-tagger", json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    if response.status_code == 200:
        session_id = response.json().get('sessionId')
        print(f"\nCheckout URL: {response.json().get('url')}")
        return session_id
    return None

if __name__ == "__main__":
    test_subscription() 