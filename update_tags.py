import requests
import json
import base64
from dotenv import load_dotenv
import os

def get_headers(api_key):
    """Create headers for Follow Up Boss API"""
    auth_string = f"{api_key}:"
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    return {
        'Authorization': f'Basic {base64_auth}',
        'Content-Type': 'application/json'
    }

def update_lead_tags(api_key):
    """Update all leads with City: tags to Zillow City: tags"""
    print("Starting tag update process...")
    
    # Get all leads
    endpoint = "https://api.followupboss.com/v1/people"
    headers = get_headers(api_key)
    all_leads = []
    offset = 0
    limit = 100
    updated_count = 0
    
    while True:
        params = {
            'source': 'Zillow',  # Only get Zillow leads
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            leads = data.get('people', [])
            
            if not leads:
                break
                
            print(f"Processing {len(leads)} leads...")
            
            # Process each lead
            for lead in leads:
                lead_id = lead.get('id')
                tags = lead.get('tags', [])
                
                if isinstance(tags, str):
                    tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                
                # Look for City: tags
                new_tags = []
                updated = False
                for tag in tags:
                    if tag.startswith('City: '):
                        city = tag.replace('City: ', '')
                        new_tag = f'Zillow City: {city}'
                        new_tags.append(new_tag)
                        updated = True
                    else:
                        new_tags.append(tag)
                
                # Update lead if tags were changed
                if updated:
                    update_data = {'tags': new_tags}
                    update_response = requests.put(
                        f"{endpoint}/{lead_id}",
                        headers=headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"Updated lead {lead_id}")
                        updated_count += 1
                    else:
                        print(f"Failed to update lead {lead_id}: {update_response.status_code}")
            
            # Check if we've reached the end
            if len(leads) < limit:
                break
                
            offset += limit
        else:
            print(f"Error getting leads: {response.status_code}")
            print(f"Response: {response.text}")
            break
    
    print(f"\nSuccessfully updated {updated_count} leads with new tag format")
    return updated_count

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('FOLLOWUP_API_KEY')
    if api_key:
        update_lead_tags(api_key)
    else:
        print("Please set FOLLOWUP_API_KEY in .env file") 