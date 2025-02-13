import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import Database
from dotenv import load_dotenv

load_dotenv()

def check_account(email):
    print(f"\nChecking account status for {email}...")
    
    # Check if user exists
    user = Database.get_user_by_email(email)
    if user:
        print(f"User found with ID: {user.id}")
        
        # Get subscription info
        subscription_data = Database.get_user_subscription(user.id)
        if subscription_data.data:
            subscription = subscription_data.data[0]
            print("\nSubscription Details:")
            print(f"Status: {subscription['status']}")
            print(f"Stripe Customer ID: {subscription['stripe_customer_id']}")
            print(f"Stripe Subscription ID: {subscription['stripe_subscription_id']}")
            print(f"Follow Up Boss API Key: {'Set' if subscription['followupboss_api_key'] else 'Not Set'}")
        else:
            print("\nNo subscription found for this user")
    else:
        print("No user account found with this email")

if __name__ == "__main__":
    check_account("adam@saahomes.com") 