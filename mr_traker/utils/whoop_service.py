import requests
from django.utils import timezone
from datetime import timedelta
from django.conf import settings  # Assuming you store client ID/Secret here

# Configuration (Add these to your settings.py)
WHOOP_CLIENT_ID = getattr(settings, 'WHOOP_CLIENT_ID', 'your_client_id')
WHOOP_CLIENT_SECRET = getattr(
    settings, 'WHOOP_CLIENT_SECRET', 'your_client_secret')
WHOOP_TOKEN_URL = "https://api.prod.whoop.com/oauth/token"


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
        print(
            f"Token expired for {athlete_profile.user.username}. Refreshing...")
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
        'scope': 'offline read:recovery read:cycles read:sleep read:workout'
    }

    try:
        response = requests.post(WHOOP_TOKEN_URL, data=payload)
        response.raise_for_status()  # Raise error if request fails

        data = response.json()

        # UPDATE THE DB
        athlete_profile.whoop_access_token = data['access_token']
        # Always rotate refresh tokens too
        athlete_profile.whoop_refresh_token = data['refresh_token']

        # Calculate new expiry (expires_in is usually seconds, e.g., 3600)
        expires_in = data.get('expires_in', 3600)
        athlete_profile.whoop_token_expires_at = timezone.now() + \
            timedelta(seconds=expires_in)

        athlete_profile.save()

        return athlete_profile.whoop_access_token

    except requests.exceptions.RequestException as e:
        print(f"Failed to refresh token: {e}")
        # Logic to handle disconnection (maybe send email to user to re-login)
        return None
