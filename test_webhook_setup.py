import os
from dotenv import load_dotenv
from src.services.zillow_lead_tagger import setup_webhook

def test_webhook_setup():
    """Test the webhook setup functionality"""
    load_dotenv()
    
    # Get the API key from .env
    api_key = os.getenv('FOLLOWUPBOSS_API_KEY')
    if not api_key:
        print("Error: No FOLLOWUPBOSS_API_KEY found in .env file")
        return False
    
    print(f"Testing webhook setup with API key: {api_key[:5]}...")
    
    # Attempt to set up the webhook
    webhook_id = setup_webhook(api_key)
    
    if webhook_id:
        print(f"✅ Success! Webhook created/found with ID: {webhook_id}")
        return True
    else:
        print("❌ Failed to create webhook")
        return False

if __name__ == "__main__":
    test_webhook_setup() 