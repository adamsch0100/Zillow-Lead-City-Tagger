import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import Database
from dotenv import load_dotenv

load_dotenv()

def create_admin_subscription(email):
    print(f"\nCreating admin subscription for {email}...")
    
    # Get user
    user = Database.get_user_by_email(email)
    if not user:
        print("User not found!")
        return False
    
    print(f"User ID: {user.id}")
    
    # Check if subscription exists
    subscription_data = Database.get_user_subscription(user.id)
    if subscription_data.data:
        print("Subscription already exists!")
        return True
    
    # Create subscription with admin privileges
    try:
        subscription = Database.create_subscription(
            user_id=user.id,
            stripe_subscription_id='admin_subscription',
            stripe_customer_id='admin_customer',
            status='active'
        )
        print("Admin subscription created successfully!")
        return True
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        return False

if __name__ == "__main__":
    create_admin_subscription("adam@saahomes.com") 