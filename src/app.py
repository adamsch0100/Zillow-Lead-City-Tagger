from flask import Flask, request, jsonify, url_for, render_template, redirect, flash
from datetime import datetime
import json
import os
import stripe
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from src.models.database import Database, User
from src.services.city_tagger_service import city_tagger_service
from dotenv import load_dotenv
import bcrypt
import base64
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
# Enable CORS for e8solutions.io
CORS(app, resources={
    r"/subscribe/*": {"origins": ["https://e8solutions.io", "http://localhost:3000"]},
    r"/billing/*": {"origins": ["*"]}  # Stripe can send webhooks from various IPs
})

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Start the city tagger service
city_tagger_service.start()

@login_manager.user_loader
def load_user(user_id):
    return Database.get_user_by_id(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Database.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's subscription
    subscription_data = Database.get_user_subscription(current_user.id)
    subscription = subscription_data.data[0] if subscription_data.data else None
    
    if not subscription:
        flash('No active subscription found', 'error')
        return redirect(url_for('subscribe_city_tagger'))
    
    # Get execution history
    executions_data = Database.get_subscription_executions(subscription['id'])
    executions = executions_data.data if executions_data.data else []
    
    return render_template('dashboard.html', 
                         subscription=subscription,
                         executions=executions)

@app.route('/settings', methods=['GET'])
@login_required
def settings():
    subscription_data = Database.get_user_subscription(current_user.id)
    subscription = subscription_data.data[0] if subscription_data.data else None
    
    if not subscription:
        flash('No active subscription found', 'error')
        return redirect(url_for('subscribe_city_tagger'))
    
    return render_template('settings.html', subscription=subscription)

@app.route('/settings/api-key', methods=['POST'])
@login_required
def update_api_key():
    api_key = request.form.get('api_key')
    if not api_key:
        flash('API key is required', 'error')
        return redirect(url_for('settings'))
    
    subscription_data = Database.get_user_subscription(current_user.id)
    if subscription_data.data:
        subscription = subscription_data.data[0]
        Database.update_followupboss_api_key(subscription['id'], api_key)
        flash('API key updated successfully', 'success')
    else:
        flash('No active subscription found', 'error')
    
    return redirect(url_for('settings'))

@app.route('/settings/password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required', 'error')
        return redirect(url_for('settings'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('settings'))
    
    if bcrypt.checkpw(current_password.encode('utf-8'), current_user.password_hash.encode('utf-8')):
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        Database.update_user_password(current_user.id, new_password_hash)
        flash('Password updated successfully', 'success')
    else:
        flash('Current password is incorrect', 'error')
    
    return redirect(url_for('settings'))

@app.route('/webhook/followupboss', methods=['POST'])
def followupboss_webhook():
    try:
        # Log receipt of webhook data
        app.logger.info("Received Follow Up Boss webhook data")
        data = request.json
        
        # Verify the request signature if provided
        signature = request.headers.get('FUB-Signature')
        if signature and not app.config.get('TESTING'):
            # TODO: Implement signature verification when X-System-Key is available
            pass
        
        # Extract event information
        event_id = data.get('eventId')
        event_type = data.get('event')
        resource_ids = data.get('resourceIds', [])
        resource_uri = data.get('uri')
        
        app.logger.info(f"Event: {event_type}, IDs: {resource_ids}")
        
        if event_type != 'peopleCreated':
            return jsonify({'status': 'ignored'}), 200
            
        # Check authentication
        subscription_id = None
        if not app.config.get('TESTING'):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Basic '):
                return jsonify({'error': 'Missing or invalid Authorization header'}), 401
                
            # Decode base64 auth
            try:
                auth_decoded = base64.b64decode(auth_header.split(' ')[1]).decode('ascii')
                api_key = auth_decoded.split(':')[0]  # Format is "api_key:"
                
                subscription = Database.get_subscription_by_api_key(api_key).data[0] if Database.get_subscription_by_api_key(api_key).data else None
                if not subscription:
                    return jsonify({'error': 'Invalid API key'}), 401
                subscription_id = subscription.get('id')
                app.logger.info(f"Found subscription ID: {subscription_id}")
            except Exception as e:
                app.logger.error(f"Authentication error: {str(e)}")
                return jsonify({'error': 'Invalid authentication format'}), 401
        
        # Process each lead in the resourceIds
        success_count = 0
        for lead_id in resource_ids:
            try:
                api_key = os.getenv('FOLLOWUPBOSS_API_KEY')
                if not api_key:
                    return jsonify({'error': 'Follow Up Boss API key not configured'}), 500
                    
                # Process lead in test mode or with valid subscription
                if app.config.get('TESTING') or subscription_id:
                    app.logger.info(f"Processing lead {lead_id}")
                    if city_tagger_service.process_new_lead(lead_id, api_key):
                        success_count += 1
                        
            except Exception as e:
                app.logger.error(f"Error processing lead {lead_id}: {str(e)}")
                continue
        
        if success_count > 0:
            return jsonify({'status': 'success', 'leads_processed': len(resource_ids), 'leads_tagged': success_count}), 200
        else:
            return jsonify({'error': 'Failed to process leads - no cities found'}), 500
            
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': f'Failed to process leads: {str(e)}'}), 500

@app.route('/subscribe/city-tagger', methods=['GET'])
def subscribe_city_tagger_page():
    """Display the subscription page"""
    return render_template('subscribe.html')

@app.route('/subscribe/city-tagger', methods=['POST'])
def subscribe_city_tagger():
    """Handle new city tagger subscription"""
    data = request.json
    
    if not data or 'priceId' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Use test key if in test mode
        is_test = data.get('isTest', False)
        if is_test:
            stripe.api_key = os.getenv('STRIPE_TEST_SECRET_KEY')
            valid_price_id = os.getenv('STRIPE_TEST_PRICE_ID')
        else:
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            valid_price_id = os.getenv('STRIPE_LIVE_PRICE_ID')
        
        # Validate price ID
        if data['priceId'] != valid_price_id:
            return jsonify({'error': f'Invalid price ID. Expected: {valid_price_id}'}), 400
            
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': data['priceId'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.getenv('E8SCRIPTS_URL', 'https://e8scripts.io') + '/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=os.getenv('E8SOLUTIONS_URL', 'https://e8solutions.io') + '/products/city-tagger?canceled=true',
            metadata={
                'source': data.get('source', 'e8solutions'),
                'is_test': is_test
            }
        )
        
        return jsonify({
            'sessionId': checkout_session.id,
            'publicKey': os.getenv('STRIPE_PUBLIC_KEY'),
            'url': checkout_session.url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/billing/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # Skip signature verification in test mode
    is_test = request.headers.get('X-Test-Mode') == 'true'
    webhook_secret = os.getenv('STRIPE_TEST_WEBHOOK_SECRET') if is_test else os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not is_test:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            app.logger.error(f"Invalid payload: {str(e)}")
            return jsonify({'error': 'Invalid payload'}), 400
        except stripe.error.SignatureVerificationError as e:
            app.logger.error(f"Invalid signature: {str(e)}")
            return jsonify({'error': 'Invalid signature'}), 400
    else:
        event = json.loads(payload)
    
    try:
        app.logger.info(f"Processing Stripe event: {event['type']}")
        
        if event['type'] == 'checkout.session.completed':
            session_obj = event['data']['object']
            
            # Check if user exists
            user = Database.get_user_by_email(session_obj['customer_email'])
            
            if not user:
                # Create new user
                temp_password = os.urandom(8).hex()
                password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                user = Database.create_user(session_obj['customer_email'], password_hash)
                
                # Send welcome email with temporary password
                msg = Message(
                    'Welcome to Zillow Showing Request City Tagger',
                    sender=os.getenv('MAIL_DEFAULT_SENDER'),
                    recipients=[session_obj['customer_email']]
                )
                msg.html = f"""
                Welcome to E8Scripts City Tagger!<br><br>
                Your temporary login credentials:<br>
                Email: {session_obj['customer_email']}<br>
                Password: {temp_password}<br><br>
                Please login at {os.getenv('E8SCRIPTS_URL')}/login to change your password and set up your Follow Up Boss API key.
                """
                if not is_test:  # Don't send emails in test mode
                    mail.send(msg)
            
            # Create subscription
            subscription = Database.create_subscription(
                user_id=user.id,
                stripe_subscription_id=session_obj['subscription'],
                stripe_customer_id=session_obj['customer'],
                status='active'
            )
            
            # Send subscription confirmation email
            msg = Message(
                'Subscription Confirmation - City Tagger',
                sender=os.getenv('MAIL_DEFAULT_SENDER'),
                recipients=[session_obj['customer_email']]
            )
            msg.html = f"""
            Thank you for subscribing to City Tagger!<br><br>
            Your subscription is now active. Please login to your dashboard at {os.getenv('E8SCRIPTS_URL')}/login
            to complete your setup and start tagging your Zillow leads.
            """
            if not is_test:  # Don't send emails in test mode
                mail.send(msg)
            
            app.logger.info(f"Successfully processed checkout session for {session_obj['customer_email']}")
            
        elif event['type'] == 'customer.subscription.updated':
            subscription_obj = event['data']['object']
            Database.update_subscription_status(
                subscription_obj['id'],
                subscription_obj['status']
            )
            app.logger.info(f"Updated subscription {subscription_obj['id']} status to {subscription_obj['status']}")
                
        elif event['type'] == 'customer.subscription.deleted':
            subscription_obj = event['data']['object']
            Database.update_subscription_status(
                subscription_obj['id'],
                'canceled'
            )
            app.logger.info(f"Canceled subscription {subscription_obj['id']}")
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 