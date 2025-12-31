import requests
from django.utils import timezone
from datetime import timedelta
from django.conf import settings  # Assuming you store client ID/Secret here

# Configuration (Add these to your settings.py)
WHOOP_CLIENT_ID = getattr(settings, 'WHOOP_CLIENT_ID', 'your_client_id')
WHOOP_CLIENT_SECRET = getattr(
    settings, 'WHOOP_CLIENT_SECRET', 'your_client_secret')
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
WHOOP_REDIRECT_URI = getattr(settings, 'WHOOP_REDIRECT_URI', 'http://127.0.0.1:8000/api/users/whoop/callback/')


def get_valid_access_token(athlete_profile):
    """
    Returns a valid access token. 
    Refreshes it automatically if it has expired.
    """

    # 1. Check if token exists
    if not athlete_profile.whoop_access_token:
        return None  # User hasn't connected WHOOP yet

    # 2. Check if expired (we add a 5-minute buffer to be safe)
    now = timezone.now()
    if athlete_profile.whoop_token_expires_at and now >= (athlete_profile.whoop_token_expires_at - timedelta(minutes=5)):
        print(f"Token expired for {athlete_profile.user.username}. Refreshing...")
        return refresh_whoop_token(athlete_profile)

    # 3. Token is still good
    return athlete_profile.whoop_access_token


def refresh_whoop_token(athlete_profile):
    """
    Hits the WHOOP API with the Refresh Token to get a fresh Access Token.
    Updates the database automatically.
    """
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': athlete_profile.whoop_refresh_token,
        'client_id': WHOOP_CLIENT_ID,
        'client_secret': WHOOP_CLIENT_SECRET,
        'scope': 'offline read:profile read:recovery read:cycles read:sleep read:workout'
    }

    import time

    max_retries = 3
    base_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(WHOOP_TOKEN_URL, data=payload)
            
            # If server error (5xx), raise to retry
            if 500 <= response.status_code < 600:
                print(f"Server error {response.status_code} refreshing token. Attempt {attempt+1}/{max_retries}")
                response.raise_for_status()

            # For 4xx errors, we should NOT retry as the payload/grant is likely invalid
            if 400 <= response.status_code < 500:
                print(f"Client error {response.status_code} refreshing token. Not retrying.")
                response.raise_for_status()

            data = response.json()

            # UPDATE THE DB
            athlete_profile.whoop_access_token = data['access_token']
            # Always rotate refresh tokens too
            athlete_profile.whoop_refresh_token = data['refresh_token']
            
            # User ID might be returned?
            if 'user_id' in data:
                 athlete_profile.whoop_user_id = data['user_id']

            # Calculate new expiry (expires_in is usually seconds, e.g., 3600)
            expires_in = data.get('expires_in', 3600)
            athlete_profile.whoop_token_expires_at = timezone.now() + \
                timedelta(seconds=expires_in)

            athlete_profile.save()

            return athlete_profile.whoop_access_token
        
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Failed to refresh token (Attempt {attempt+1}): {e}")
            if 'response' in locals() and response is not None:
                # If we are here because of 4xx raise_for_status above, break
                if 400 <= response.status_code < 500:
                    print(f"DEBUG: Critical Client Error: {response.content}")
                    break
                
                print(f"DEBUG: Refresh Error Content: {response.content}")
            
            # Backoff before retry if not last attempt
            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt)
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("Max retries reached. Token refresh failed.")
                return None


def exchange_oauth_code(code):
    """
    Exchanges the temporary authorization code for an access token and refresh token.
    """
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': WHOOP_CLIENT_ID,
        'client_secret': WHOOP_CLIENT_SECRET,
        'redirect_uri': WHOOP_REDIRECT_URI,
        # 'scope': ... # Scope is usually defined in the initial authorization request
    }

    try:
        response = requests.post(WHOOP_TOKEN_URL, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to exchange code: {e}")
        if response is not None:
             print(f"Response content: {response.content}")
        return None


def get_user_profile(access_token):
    """
    Fetches the basic user profile from WHOOP.
    required scope: offline (or read:profile if available, but offline seems standard for basic profile)
    """
    url = "https://api.prod.whoop.com/developer/v1/user/profile/basic"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get user profile: {e}")
        if 'response' in locals():
             print(f"Response content: {response.content}")
        return None


def get_workout_by_id(access_token, workout_id):
    """
    Fetches a single workout by ID.
    Using V2 API.
    """
    url = f"https://api.prod.whoop.com/developer/v2/activity/workout/{workout_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get workout {workout_id}: {e}")
        if 'response' in locals():
             print(f"Response content: {response.content}")
        return None


def get_sleep_by_id(access_token, sleep_id):
    """
    Fetches a single sleep record by ID (UUID).
    """
    url = f"https://api.prod.whoop.com/developer/v2/activity/sleep/{sleep_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get sleep {sleep_id}: {e}")
        if 'response' in locals():
             print(f"Response content: {response.content}")
        return None


def get_recovery_by_cycle_id(access_token, cycle_id):
    """
    Fetches recovery data for a specific cycle ID.
    """
    url = f"https://api.prod.whoop.com/developer/v2/cycle/{cycle_id}/recovery"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get recovery for cycle {cycle_id}: {e}")
        if 'response' in locals():
             print(f"Response content: {response.content}")
        return None
