from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.dateparse import parse_datetime
import requests

from .models import Workout
from .serializers import WorkoutSerializer
from users.models import User
from utils.whoop_service import get_valid_access_token

class WorkoutListView(APIView):
    """
    GET /api/workouts/
    Fetches latest workouts from WHOOP and returns them.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Get the Athlete Profile
        user = request.user
        
        # Helper: if trainer, allow specifying athlete_id? (SKIP FOR NOW, assume user is athlete)
        if not hasattr(user, 'athlete_profile'):
             return Response({"detail": "User is not an athlete."}, status=status.HTTP_400_BAD_REQUEST)
        
        profile = user.athlete_profile

        # 2. Get Valid Token (Refresh if needed)
        access_token = get_valid_access_token(profile)
        if not access_token:
            return Response({"detail": "WHOOP not connected or token expired."}, status=status.HTTP_401_UNAUTHORIZED)

        # 3. Fetch from WHOOP API
        # v1 endpoint: https://api.prod.whoop.com/v1/activity/workout
        # limit is optional, default 25
        url = "https://api.prod.whoop.com/v1/activity/workout?limit=25" 
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            workouts_data = response.json() # List of workouts
        except requests.exceptions.RequestException as e:
            return Response({"detail": f"Failed to fetch workouts from WHOOP: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        # 4. Sync to DB
        synced_workouts = []
        for item in workouts_data:
            score = item.get('score', {})
            
            workout, created = Workout.objects.update_or_create(
                whoop_id=item['id'],
                defaults={
                    'athlete': profile,
                    'start': parse_datetime(item['start']),
                    'end': parse_datetime(item['end']),
                    'timezone_offset': item.get('timezone_offset'),
                    'sport_id': item.get('sport_id'),
                    'score_state': item.get('score_state'),
                    # Score fields
                    'strain': score.get('strain'),
                    'average_heart_rate': score.get('average_heart_rate'),
                    'max_heart_rate': score.get('max_heart_rate'),
                    'kilojoule': score.get('kilojoule'),
                    'percent_recorded': score.get('percent_recorded'),
                    'distance_meter': score.get('distance_meter'),
                    'altitude_gain_meter': score.get('altitude_gain_meter'),
                    'altitude_change_meter': score.get('altitude_change_meter'),
                }
            )
            synced_workouts.append(workout)

        # 5. Return from DB (ordered by start desc)
        serializer = WorkoutSerializer(synced_workouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
