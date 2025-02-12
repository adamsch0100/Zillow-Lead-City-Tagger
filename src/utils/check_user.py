from database import Database

def check_user(email):
    print(f"\nChecking user: {email}")
    user = Database.get_user_by_email(email)
    print(f"User exists: {user is not None}")
    
    if user:
        subscription = Database.get_user_subscription(user.id)
        print(f"Subscription data: {subscription.data if subscription else None}")
        
if __name__ == "__main__":
    check_user("adam@saahomes.com") 