import os
from dotenv import load_dotenv
from src.models.database import Database

def clear_execution_history(email='adam@saahomes.com'):
    """Clear all execution history for a specific user"""
    load_dotenv()
    
    print(f"Finding user with email: {email}")
    user = Database.get_user_by_email(email)
    
    if not user:
        print(f"❌ No user found with email: {email}")
        return False
    
    print(f"Found user: {user.id} - {user.email}")
    
    # Get subscription for user
    print("Finding subscription...")
    subscription_data = Database.get_user_subscription(user.id)
    subscription = subscription_data.data[0] if subscription_data.data else None
    
    if not subscription:
        print("❌ No active subscription found for this user")
        return False
    
    print(f"Found subscription: {subscription['id']}")
    
    # Get current execution history
    executions_data = Database.get_subscription_executions(subscription['id'])
    executions = executions_data.data if executions_data.data else []
    
    print(f"Found {len(executions)} execution records")
    
    # Delete each execution record
    if executions:
        for execution in executions:
            print(f"Deleting execution {execution['id']} from {execution['created_at']}")
            result = Database.delete_script_execution(execution['id'])
            if result:
                print(f"✅ Successfully deleted execution {execution['id']}")
            else:
                print(f"❌ Failed to delete execution {execution['id']}")
    
    print("\nExecution history has been cleared")
    return True

if __name__ == "__main__":
    clear_execution_history() 