from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.dateparse import parse_datetime
import requests

from .models import Sleep
from .serializers import SleepSerializer
from utils.whoop_service import get_valid_access_token

class SleepListView(APIView):
    """
    GET /api/sleep/
    Fetches latest sleep data from WHOOP and returns them.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Get the Athlete Profile
        user = request.user
        if not hasattr(user, 'athlete_profile'):
             return Response({"detail": "User is not an athlete."}, status=status.HTTP_400_BAD_REQUEST)
        
        profile = user.athlete_profile

        # 2. Get Valid Token
        access_token = get_valid_access_token(profile)
        if not access_token:
            return Response({"detail": "WHOOP not connected or token expired."}, status=status.HTTP_401_UNAUTHORIZED)

        # 3. Fetch from WHOOP API
        limit = request.query_params.get('limit', 25)
        # Trying /activity/sleep/ endpoint as /sleep/ returned 404
        url = f"https://api.prod.whoop.com/developer/v2/activity/sleep?limit={limit}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
             
            # V2 returns a paginated response wrapper { "records": [...], "next_token": ... }
            if isinstance(data, dict) and 'records' in data:
                 data = data['records']

        except requests.exceptions.RequestException as e:
            return Response({"detail": f"Failed to fetch sleep from WHOOP: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        # 4. Sync to DB
        synced_sleeps = []
        for item in data:
            score = item.get('score', {})
            
            # Use whoop_id (the API 'id') as the unique identifier
            sleep_obj, created = Sleep.objects.update_or_create(
                whoop_id=item['id'],
                defaults={
                    'athlete': profile,
                    'whoop_user_id': item['user_id'],
                    'cycle_id': item['cycle_id'],
                    'created_at': parse_datetime(item['created_at']),
                    'updated_at': parse_datetime(item['updated_at']),
                    'start': parse_datetime(item['start']),
                    'end': parse_datetime(item['end']),
                    'timezone_offset': item['timezone_offset'],
                    'nap': item['nap'],
                    'score_state': item['score_state'],
                    'score': score,
                    'is_cutting_weight': profile.is_weight_cutting,
                }
            )
            synced_sleeps.append(sleep_obj)

        # 5. Return from DB (ordered by start desc usually, but we append in order of API response)
        # API usually returns newest first.
        serializer = SleepSerializer(synced_sleeps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LatestSleepView(APIView):
    """
    GET /api/sleep/latest/
    Returns the single latest sleep record for the user (by end time) from the local DB.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'athlete_profile'):
             return Response({"detail": "User is not an athlete."}, status=status.HTTP_400_BAD_REQUEST)
        
        profile = user.athlete_profile

        # Get the sleep with the latest 'end' time
        latest_sleep = Sleep.objects.filter(athlete=profile).order_by('-end').first()

        if not latest_sleep:
            return Response({"detail": "No sleep data found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SleepSerializer(latest_sleep)
        return Response(serializer.data, status=status.HTTP_200_OK)
