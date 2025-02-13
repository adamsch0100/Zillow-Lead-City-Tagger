from supabase import create_client
import os
from dotenv import load_dotenv
from flask_login import UserMixin

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("Missing required Supabase environment variables")

supabase = create_client(supabase_url, supabase_key)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.created_at = user_data['created_at']
        self.updated_at = user_data['updated_at']

class Database:
    @staticmethod
    def create_user(email, password_hash):
        if not email or not password_hash:
            return None
            
        try:
            result = supabase.table('users').insert({
                'email': email,
                'password_hash': password_hash
            }).execute()
            
            if result.data and len(result.data) > 0:
                return User(result.data[0])
            return None
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_email(email):
        result = supabase.table('users').select('*').eq('email', email).execute()
        if result.data:
            return User(result.data[0])
        return None

    @staticmethod
    def get_user_by_id(user_id):
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        if result.data:
            return User(result.data[0])
        return None

    @staticmethod
    def update_user_password(user_id, password_hash):
        return supabase.table('users').update({
            'password_hash': password_hash
        }).eq('id', user_id).execute()

    @staticmethod
    def create_subscription(user_id, stripe_subscription_id, stripe_customer_id, status):
        return supabase.table('subscriptions').insert({
            'user_id': user_id,
            'stripe_subscription_id': stripe_subscription_id,
            'stripe_customer_id': stripe_customer_id,
            'status': status
        }).execute()

    @staticmethod
    def update_subscription_status(stripe_subscription_id, status):
        return supabase.table('subscriptions').update({
            'status': status
        }).eq('stripe_subscription_id', stripe_subscription_id).execute()

    @staticmethod
    def get_user_subscription(user_id):
        return supabase.table('subscriptions').select('*').eq('user_id', user_id).execute()

    @staticmethod
    def create_script_execution(subscription_id, status):
        return supabase.table('script_executions').insert({
            'subscription_id': subscription_id,
            'status': status
        }).execute()

    @staticmethod
    def update_script_execution(execution_id, status, leads_processed=None, cities_tagged=None, error_message=None):
        update_data = {'status': status}
        if leads_processed is not None:
            update_data['leads_processed'] = leads_processed
        if cities_tagged is not None:
            update_data['cities_tagged'] = cities_tagged
        if error_message is not None:
            update_data['error_message'] = error_message
        
        return supabase.table('script_executions').update(update_data).eq('id', execution_id).execute()

    @staticmethod
    def get_subscription_executions(subscription_id):
        return supabase.table('script_executions').select('*').eq('subscription_id', subscription_id).order('created_at', desc=True).limit(50).execute()

    @staticmethod
    def get_active_subscriptions():
        return supabase.table('subscriptions').select('*').eq('status', 'active').execute()

    @staticmethod
    def update_followupboss_api_key(subscription_id, api_key):
        return supabase.table('subscriptions').update({
            'followupboss_api_key': api_key
        }).eq('id', subscription_id).execute()

    @staticmethod
    def get_subscription_by_api_key(api_key):
        return supabase.table('subscriptions').select('*').eq('followupboss_api_key', api_key).execute() 