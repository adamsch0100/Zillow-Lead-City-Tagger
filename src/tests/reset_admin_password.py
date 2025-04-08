import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.database import Database
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def reset_admin_password(email, new_password):
    print(f"\nResetting password for {email}...")
    
    # Get user
    user = Database.get_user_by_email(email)
    if not user:
        print("User not found! Creating new user...")
        # Hash password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Create user
        user = Database.create_user(email, password_hash)
        if not user:
            print("Failed to create user!")
            return False
        print("User created successfully!")
    else:
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Update password
        result = Database.update_user_password(user.id, password_hash)
        if not result:
            print("Failed to update password")
            return False
        print("Password updated successfully!")
    
    print(f"Email: {email}")
    print(f"Password: {new_password}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_admin_password.py <email> <new_password>")
        sys.exit(1)
        
    email = sys.argv[1]
    new_password = sys.argv[2]
    reset_admin_password(email, new_password) 