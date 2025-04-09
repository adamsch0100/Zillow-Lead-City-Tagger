import requests
import json
import base64
from datetime import datetime, timedelta
import re
import os

def get_headers(api_key):
    """Create headers for Follow Up Boss API"""
    auth_string = f"{api_key}:"  # Note the colon at the end
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    return {
        'Authorization': f'Basic {base64_auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-System': 'city_tagger'  # Required system identifier
    }

def setup_webhook(api_key):
    """Set up webhook in Follow Up Boss"""
    if not api_key or not isinstance(api_key, str) or len(api_key) < 10:
        print(f"Invalid API key format: {api_key}")
        return None
        
    headers = get_headers(api_key)
    endpoint = "https://api.followupboss.com/v1/webhooks"
    
    # Get webhook domain from environment
    webhook_domain = os.getenv('E8SCRIPTS_URL', 'https://e8scripts.io')
    
    # Configure webhook
    data = {
        "url": f"{webhook_domain}/webhook/followupboss",
        "events": ["peopleCreated"],
        "isActive": True,
        "name": "City Tagger Service",
        "system": "city_tagger"  # Match the X-System header
    }
    
    # First, check if webhook already exists
    try:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            webhooks = response.json()
            if isinstance(webhooks, list):
                for webhook in webhooks:
                    if webhook.get('name') == "City Tagger Service":
                        print(f"Webhook already exists with ID: {webhook['id']}")
                        return webhook['id']
        
        # Create new webhook if it doesn't exist
        response = requests.post(endpoint, headers=headers, json=data)
        if response.status_code == 200:
            webhook_id = response.json().get('id')
            print(f"Created new webhook with ID: {webhook_id}")
            return webhook_id
        
        print(f"Failed to create webhook: {response.status_code}")
        print(f"Response: {response.text}")
        return None
        
    except Exception as e:
        print(f"Error setting up webhook: {str(e)}")
        return None

def get_zillow_leads(api_key):
    """Get all leads from Follow Up Boss with source 'Zillow'"""
    endpoint = "https://api.followupboss.com/v1/people"
    headers = get_headers(api_key)
    all_leads = []
    offset = 0
    limit = 100  # Max limit per request
    
    while True:
        params = {
            'source': 'Zillow',
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            leads = data.get('people', [])
            
            if not leads:  # No more leads to fetch
                break
                
            all_leads.extend(leads)
            print(f"Fetched {len(leads)} leads (total so far: {len(all_leads)})")
            
            # Check if we've reached the end
            if len(leads) < limit:
                break
                
            offset += limit
        else:
            print(f"Error getting leads: {response.status_code}")
            print(f"Response: {response.text}")
            break
    
    print(f"Total Zillow leads found: {len(all_leads)}")
    return all_leads

def extract_city_from_address(address_data):
    """Extract and validate city from address data"""
    if not address_data:
        return None
        
    # If we have a direct city field, use it
    if 'city' in address_data:
        city = address_data['city'].strip().title()
        print(f"Found city in address data: {city}")
        return city
        
    # If we have a full address, try to extract city
    if 'full_address' in address_data:
        full_address = address_data['full_address'].lower()
        city_pattern = r'(?:greeley|fort morgan|wiggins|woodland park|cheyenne)'
        city_match = re.search(city_pattern, full_address)
        if city_match:
            city = city_match.group(0).title()
            print(f"Extracted city from full address: {city}")
            return city
            
    return None

def update_lead_tags(lead_id, city, api_key):
    """Update lead tags in Follow Up Boss"""
    print(f"\nUpdating tags for lead {lead_id} with city {city}")
    headers = get_headers(api_key)
    endpoint = f"https://api.followupboss.com/v1/people/{lead_id}"
    
    # Get current tags
    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        print(f"Error getting lead: {response.status_code}")
        print(f"Response: {response.text}")
        return False
        
    lead_data = response.json()
    current_tags = lead_data.get('tags', [])
    
    # Create new tag
    zillow_city_tag = f"Zillow City: {city}"
    
    # Check if Zillow city tag already exists
    if any(tag.startswith("Zillow City:") for tag in current_tags):
        print("Lead already has a Zillow City tag")
        return True  # Count this as a success since the lead is properly tagged
        
    # Add new tag
    new_tags = current_tags + [zillow_city_tag]
    
    # Update lead
    update_data = {'tags': new_tags}
    response = requests.put(endpoint, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print(f"Successfully updated lead {lead_id} with Zillow City tag")
        return True
    else:
        print(f"Error updating lead: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def get_property_from_lead(lead_id, api_key):
    """Get property information from events and lead data"""
    print(f"\nGetting events for lead {lead_id}")
    headers = get_headers(api_key)
    
    # Define patterns for property inquiry formats
    property_patterns = [
        r'interested in\s+([^\.]+)',
        r'property inquiry:?\s+([^\.]+)',
        r'viewed\s+([^\.]+)',
        r'looking at\s+([^\.]+)',
        r'inquired about\s+([^\.]+)',
        r'property:\s+([^\.]+)',
        r'address:\s+([^\.]+)',
        r'interested in seeing\s+([^\.]+)'
    ]
    
    # Define city pattern
    city_pattern = r'(?:greeley|fort morgan|wiggins|woodland park|cheyenne)'
    
    # Get the lead data to check source data and notes
    lead_endpoint = f"https://api.followupboss.com/v1/people/{lead_id}"
    lead_response = requests.get(lead_endpoint, headers=headers)
    if lead_response.status_code != 200:
        print(f"Error getting lead data: {lead_response.status_code}")
        print(f"Response: {lead_response.text}")
        return None
        
    lead_data = lead_response.json()
    print(f"Got lead data: {json.dumps(lead_data, indent=2)}")
    
    # Check source data
    source_data = lead_data.get('sourceData', {})
    if source_data:
        print(f"Checking source data: {str(source_data)[:200]}...")
        if 'property' in source_data:
            property_data = source_data['property']
            city = property_data.get('city')
            if city:
                address = {
                    'street': property_data.get('street', ''),
                    'city': city,
                    'state': property_data.get('state', ''),
                    'code': property_data.get('code', '')
                }
                print(f"Found property in source data: {address}")
                return address
    
    # Check notes
    notes = lead_data.get('notes', [])
    if notes:
        for note in notes:
            message = note.get('message', '')
            print(f"Checking note: {message[:200]}...")
            
            # Check for various property inquiry formats
            for pattern in property_patterns:
                address_match = re.search(pattern, message, re.IGNORECASE)
                if address_match:
                    address = address_match.group(1).strip()
                    print(f"Found address using pattern '{pattern}' in note: {address}")
                    return {'full_address': address}
            
            # Look for city names directly
            city_match = re.search(city_pattern, message.lower())
            if city_match:
                city = city_match.group(0).title()
                print(f"Found city directly in note: {city}")
                return {'city': city}
    
    # Get events for the lead
    events_endpoint = "https://api.followupboss.com/v1/events"
    params = {
        'personId': lead_id,
        'limit': 100  # Get all recent events
    }
    
    events_response = requests.get(events_endpoint, headers=headers, params=params)
    if events_response.status_code == 200:
        events_data = events_response.json()
        events = events_data.get('events', [])
        
        for event in events:
            # Print first 200 chars of event for debugging
            print(f"Processing event: {str(event)[:200]}...")
            
            # Check for property information in the event
            property_data = event.get('property', {})
            if property_data:
                city = property_data.get('city')
                if city:
                    address = {
                        'street': property_data.get('street', ''),
                        'city': city,
                        'state': property_data.get('state', ''),
                        'code': property_data.get('code', '')
                    }
                    print(f"Found property in event: {address}")
                    return address
            
            # If no property object, check the message
            message = event.get('message', '')
            if message:
                print(f"Checking message: {message[:200]}...")
                
                # Check for various property inquiry formats
                for pattern in property_patterns:
                    address_match = re.search(pattern, message, re.IGNORECASE)
                    if address_match:
                        address = address_match.group(1).strip()
                        print(f"Found address using pattern '{pattern}' in event: {address}")
                        return {'full_address': address}
                
                # Look for city names directly
                city_match = re.search(city_pattern, message.lower())
                if city_match:
                    city = city_match.group(0).title()
                    print(f"Found city directly in event: {city}")
                    return {'city': city}
    
    return None

def process_lead(lead_id, api_key):
    """Process a single lead"""
    print(f"\nProcessing lead {lead_id}")
    
    # Try to get property information from events
    address_data = get_property_from_lead(lead_id, api_key)
    
    if address_data:
        city = extract_city_from_address(address_data)
        if city:
            return update_lead_tags(lead_id, city, api_key)
    else:
        print("No property inquiry found for this lead")
    
    return False

def process_all_leads(api_key):
    """Process all Zillow leads for a subscriber"""
    print("Starting Zillow lead tagging process...")
    
    # First, ensure webhook is set up
    webhook_id = setup_webhook(api_key)
    if not webhook_id:
        print("Warning: Failed to set up webhook")
    
    # Get all Zillow leads
    leads = get_zillow_leads(api_key)
    print(f"\nProcessing {len(leads)} Zillow leads")
    
    tagged_count = 0
    for lead in leads:
        lead_id = lead.get('id')
        if process_lead(lead_id, api_key):
            tagged_count += 1
    
    print(f"\nSuccessfully tagged {tagged_count} leads with city information")
    return tagged_count

if __name__ == "__main__":
    # For testing purposes
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    api_key = os.getenv('FOLLOWUPBOSS_API_KEY')
    if api_key:
        process_all_leads(api_key)
    else:
        print("Please set FOLLOWUPBOSS_API_KEY in .env file") 