import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mr_traker.settings')
django.setup()

from users.models import AthleteProfile
from utils.whoop_service import get_valid_access_token

def test_endpoints():
    try:
        profile = AthleteProfile.objects.filter(user__username__icontains="idorabin").first()
        if not profile:
             profile = AthleteProfile.objects.first()
        
        token = get_valid_access_token(profile)
        print(f"Using profile: {profile.user.username}, Token: {token[:10]}...")
    except Exception as e:
        print(f"Profile not found: {e}")
        # Try getting any profile
        profile = AthleteProfile.objects.first()
        if profile:
            token = get_valid_access_token(profile)
            print(f"Using alternate profile: {profile.user.username}")
        else:
            print("No profiles found.")
            return

    headers = {"Authorization": f"Bearer {token}"}

    # 1. SLEEP
    print("\n--- Testing Sleep API ---")
    list_url = "https://api.prod.whoop.com/developer/v2/activity/sleep?limit=1"
    resp = requests.get(list_url, headers=headers)
    if resp.status_code == 200:
        records = resp.json().get('records', [])
        if records:
            sleep_id = records[0]['id']
            print(f"Found Sleep ID: {sleep_id}")
            # Try Fetch by ID
            single_url = f"https://api.prod.whoop.com/developer/v2/activity/sleep/{sleep_id}"
            resp2 = requests.get(single_url, headers=headers)
            print(f"Fetch Sleep by ID Status: {resp2.status_code}")
            if resp2.status_code == 200:
                print("Success fetching Sleep by ID.")
            else:
                print(f"Failed: {resp2.text}")
        else:
            print("No sleep records found.")
    else:
        print(f"Failed to list sleep: {resp.status_code}")

    # 2. RECOVERY
    print("\n--- Testing Recovery API ---")
    rec_list_url = "https://api.prod.whoop.com/developer/v2/recovery?limit=1"
    resp = requests.get(rec_list_url, headers=headers)
    if resp.status_code == 200:
        records = resp.json().get('records', [])
        if records:
            rec = records[0]
            cycle_id = rec.get('cycle_id')
            rec_id = rec.get('id') # Does it exist?
            print(f"First Recovery Record Keys: {rec.keys()}")
            print(f"Cycle ID: {cycle_id}, ID (if any): {rec_id}")

            # Try Filtering by Cycle ID
            if cycle_id:
                url_f = f"https://api.prod.whoop.com/developer/v2/recovery?cycle_id={cycle_id}"
                print(f"Testing Filter {url_f}")
                resp_f = requests.get(url_f, headers=headers)
                print(f"Result by Filter: {resp_f.status_code}")
                if resp_f.status_code == 200:
                    print(f"Items found: {len(resp_f.json().get('records', []))}")

                # Try Cycle Endpoint
                url_c2 = f"https://api.prod.whoop.com/developer/v2/cycle/{cycle_id}/recovery"
                print(f"Testing Cycle Endpoint {url_c2}")
                resp_c2 = requests.get(url_c2, headers=headers)
                print(f"Result by Cycle Endpoint: {resp_c2.status_code}")

            if rec_id:
                 pass # ID was none
                 
                 
                 
if __name__ == "__main__":
    test_endpoints()
