import os
import requests
import base64
from dotenv import load_dotenv

def clear_zillow_city_tags():
    """Remove all Zillow City tags from Follow Up Boss leads"""
    load_dotenv()
    
    # Get the API key from .env
    api_key = os.getenv('FOLLOWUPBOSS_API_KEY')
    if not api_key:
        print("Error: No FOLLOWUPBOSS_API_KEY found in .env file")
        return False
    
    # Create auth string for Basic Auth
    auth_string = f"{api_key}:"  # Note the colon at the end
    auth_bytes = auth_string.encode('ascii')
    base64_auth = base64.b64encode(auth_bytes).decode('ascii')
    
    # Configure headers
    headers = {
        'Authorization': f'Basic {base64_auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-System': 'city_tagger'  # Required system identifier
    }
    
    endpoint = "https://api.followupboss.com/v1/people"
    
    print("Getting leads from Follow Up Boss...")
    
    all_leads = []
    offset = 0
    limit = 100
    
    # Get all leads with Zillow City tags
    while True:
        params = {
            'limit': limit,
            'offset': offset,
            'tagsContains': 'Zillow City:'
        }
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            
            if response.status_code != 200:
                print(f"❌ Failed to get leads: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
            data = response.json()
            leads = data.get('people', [])
            
            if not leads:
                break
                
            all_leads.extend(leads)
            print(f"Found {len(leads)} leads with Zillow City tags (total: {len(all_leads)})")
            
            if len(leads) < limit:
                break
                
            offset += limit
                
        except Exception as e:
            print(f"Error getting leads: {str(e)}")
            return False
    
    print(f"\nFound a total of {len(all_leads)} leads with Zillow City tags")
    
    # Remove Zillow City tags from each lead
    success_count = 0
    for lead in all_leads:
        lead_id = lead.get('id')
        current_tags = lead.get('tags', [])
        
        # Filter out Zillow City tags
        new_tags = [tag for tag in current_tags if not tag.startswith('Zillow City:')]
        
        if len(new_tags) < len(current_tags):
            # Update lead with filtered tags
            try:
                update_data = {'tags': new_tags}
                response = requests.put(
                    f"{endpoint}/{lead_id}",
                    headers=headers,
                    json=update_data
                )
                
                if response.status_code == 200:
                    success_count += 1
                    print(f"✅ Removed Zillow City tags from lead {lead_id}")
                else:
                    print(f"❌ Failed to update lead {lead_id}: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"Error updating lead {lead_id}: {str(e)}")
        else:
            print(f"No Zillow City tags found for lead {lead_id} (unexpected)")
    
    print(f"\nSuccessfully removed Zillow City tags from {success_count} of {len(all_leads)} leads")
    return True

if __name__ == "__main__":
    clear_zillow_city_tags() 