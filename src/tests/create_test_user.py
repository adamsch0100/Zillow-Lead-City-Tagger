import os
from database import Database
import bcrypt
from datetime import datetime

def create_test_user():
    print("\n1. Creating test user...")
    email = "test@example.com"
    password = "testpass123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create or get user
    user = Database.get_user_by_email(email)
    if not user:
        user = Database.create_user(email, password_hash)
        print(f"Created new user: {email}")
    else:
        print(f"Using existing user: {email}")
    
    print("\n2. Setting up subscription...")
    subscription_data = Database.get_user_subscription(user.id)
    if not subscription_data.data:
        subscription = Database.create_subscription(
            user_id=user.id,
            stripe_subscription_id='sub_test123',
            stripe_customer_id='cus_test123',
            status='active'
        )
        print("Created new subscription")
    else:
        subscription = subscription_data.data[0]
        print("Using existing subscription")
    
    print("\n3. Setting Follow Up Boss API key...")
    if subscription_data.data:
        Database.update_followupboss_api_key(
            subscription_data.data[0]['id'],
            os.getenv('FOLLOWUPBOSS_API_KEY')
        )
        print("API key updated")
    
    print("\nTest user setup complete!")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("You can now log in at http://localhost:5000/login")

if __name__ == '__main__':
    create_test_user() 