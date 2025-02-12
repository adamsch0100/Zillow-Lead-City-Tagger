from database import Database
from datetime import datetime, timedelta

def create_test_executions():
    # Get the test user's subscription
    user = Database.get_user_by_email('test@example.com')
    subscription_data = Database.get_user_subscription(user.id)
    
    if not subscription_data.data:
        print("No subscription found for test user")
        return
    
    subscription_id = subscription_data.data[0]['id']
    
    # Create some test executions with different statuses and timestamps
    base_time = datetime.utcnow()
    executions = [
        {
            'status': 'completed',
            'leads_processed': 15,
            'cities_tagged': 12,
            'error_message': None,
            'created_at': (base_time - timedelta(hours=1)).isoformat()
        },
        {
            'status': 'failed',
            'leads_processed': 5,
            'cities_tagged': 3,
            'error_message': 'API rate limit exceeded',
            'created_at': (base_time - timedelta(hours=2)).isoformat()
        },
        {
            'status': 'completed',
            'leads_processed': 8,
            'cities_tagged': 8,
            'error_message': None,
            'created_at': (base_time - timedelta(hours=3)).isoformat()
        },
        {
            'status': 'running',
            'leads_processed': 2,
            'cities_tagged': 1,
            'error_message': None,
            'created_at': base_time.isoformat()
        }
    ]
    
    for execution in executions:
        result = Database.create_script_execution(
            subscription_id=subscription_id,
            status=execution['status']
        )
        if result.data:
            execution_id = result.data[0]['id']
            Database.update_script_execution(
                execution_id=execution_id,
                status=execution['status'],
                leads_processed=execution['leads_processed'],
                cities_tagged=execution['cities_tagged'],
                error_message=execution['error_message']
            )
            print(f"Created execution: {execution['status']} - {execution['leads_processed']} leads at {execution['created_at']}")

if __name__ == '__main__':
    create_test_executions() 