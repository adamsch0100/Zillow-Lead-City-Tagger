from src.models.database import Database
from src.services.zillow_lead_tagger import process_lead, process_all_leads, setup_webhook
import time
from datetime import datetime, timedelta
import threading

class CityTaggerService:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start the city tagger service"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_service)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """Stop the city tagger service"""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_service(self):
        """Main service loop - only monitors webhook health"""
        while self.running:
            try:
                # Get all active subscriptions
                subscriptions = Database.get_active_subscriptions()
                
                for subscription in subscriptions.data:
                    if not subscription['followupboss_api_key']:
                        continue

                    # Ensure webhook is set up for each subscription
                    setup_webhook(subscription['followupboss_api_key'])

            except Exception as e:
                print(f"Error in city tagger service: {str(e)}")

            # Check webhook health every 6 hours
            time.sleep(21600)

    def process_new_lead(self, lead_id, api_key):
        """Process a single new lead"""
        try:
            print(f"\nProcessing new lead {lead_id}")
            
            # Find subscription by API key
            subscription = Database.get_subscription_by_api_key(api_key).data[0]
            if not subscription:
                print(f"No subscription found for API key")
                return False
            
            # Create execution record
            execution = Database.create_script_execution(
                subscription_id=subscription['id'],
                status='running'
            ).data[0]
            
            try:
                # Process the lead
                print(f"Processing lead {lead_id} with API key {api_key}")
                from zillow_lead_tagger import process_lead
                success = process_lead(lead_id, api_key)
                
                # Update execution record
                if success:
                    Database.update_script_execution(
                        execution_id=execution['id'],
                        status='completed',
                        leads_processed=1,
                        cities_tagged=1
                    )
                    print(f"Successfully processed lead {lead_id}")
                    return True
                else:
                    Database.update_script_execution(
                        execution_id=execution['id'],
                        status='failed',
                        leads_processed=1,
                        cities_tagged=0,
                        error_message='Failed to process lead - no city found'
                    )
                    print(f"Failed to process lead {lead_id} - no city found")
                    return False
                    
            except Exception as e:
                print(f"Error processing lead {lead_id}: {str(e)}")
                Database.update_script_execution(
                    execution_id=execution['id'],
                    status='failed',
                    error_message=str(e)
                )
                raise
                
        except Exception as e:
            print(f"Error in process_new_lead: {str(e)}")
            raise

# Create singleton instance
city_tagger_service = CityTaggerService() 