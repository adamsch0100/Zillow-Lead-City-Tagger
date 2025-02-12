from database import Database
import time
from datetime import datetime, timedelta

def monitor_service():
    print("Starting City Tagger Service Monitor...")
    print("Monitoring execution history and service status...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get all active subscriptions
            subscriptions = Database.get_active_subscriptions()
            print(f"\nActive Subscriptions: {len(subscriptions.data)}")
            
            for subscription in subscriptions.data:
                print(f"\nSubscription ID: {subscription['id']}")
                print(f"Status: {subscription['status']}")
                print(f"Follow Up Boss API Key: {'✓ Set' if subscription['followupboss_api_key'] else '✗ Not Set'}")
                
                # Get recent executions
                executions = Database.get_subscription_executions(subscription['id'])
                if executions.data:
                    print("\nRecent Executions:")
                    for execution in executions.data[:5]:  # Show last 5 executions
                        status_symbol = "✓" if execution['status'] == 'completed' else "✗" if execution['status'] == 'failed' else "⋯"
                        created_at = execution['created_at'].split('.')[0].replace('T', ' ')
                        print(f"{status_symbol} [{created_at}] {execution['status'].title()}: {execution['leads_processed']} leads, {execution['cities_tagged']} cities tagged")
                        if execution['error_message']:
                            print(f"   Error: {execution['error_message']}")
                else:
                    print("No executions found")
                
                print("-" * 50)
            
            # Calculate some statistics
            total_executions = 0
            total_leads = 0
            total_cities = 0
            errors = 0
            
            for subscription in subscriptions.data:
                executions = Database.get_subscription_executions(subscription['id'])
                for execution in executions.data:
                    total_executions += 1
                    total_leads += execution['leads_processed'] or 0
                    total_cities += execution['cities_tagged'] or 0
                    if execution['status'] == 'failed':
                        errors += 1
            
            print("\nOverall Statistics:")
            print(f"Total Executions: {total_executions}")
            print(f"Total Leads Processed: {total_leads}")
            print(f"Total Cities Tagged: {total_cities}")
            print(f"Success Rate: {((total_executions - errors) / total_executions * 100) if total_executions > 0 else 0:.1f}%")
            
            print("\nWaiting 30 seconds before next update...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == '__main__':
    monitor_service() 