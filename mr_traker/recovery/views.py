from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.dateparse import parse_datetime
import requests

from .models import Recovery
from .serializers import RecoverySerializer
from utils.whoop_service import get_valid_access_token

class RecoveryListView(APIView):
    """
    GET /api/recovery/
    Fetches latest recovery data from WHOOP and returns them.
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
        # Verified URL: https://api.prod.whoop.com/developer/v2/recovery
        limit = request.query_params.get('limit', 25)
        url = f"https://api.prod.whoop.com/developer/v2/recovery?limit={limit}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
             
            # V2 returns a paginated response wrapper { "records": [...], "next_token": ... }
            if isinstance(data, dict) and 'records' in data:
                 data = data['records']

        except requests.exceptions.RequestException as e:
            return Response({"detail": f"Failed to fetch recovery from WHOOP: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        # 4. Sync to DB
        synced_recoveries = []
        for item in data:
            score = item.get('score', {})
            
            # WHOOP V2 Recovery uses cycle_id as unique identifier usually
            recovery, created = Recovery.objects.update_or_create(
                cycle_id=item['cycle_id'],
                defaults={
                    'athlete': profile,
                    'sleep_id': item.get('sleep_id'),
                    'score_state': item.get('score_state'),
                    # Score fields
                    'user_calibrating': score.get('user_calibrating', False),
                    'recovery_score': score.get('recovery_score'),
                    'resting_heart_rate': score.get('resting_heart_rate'),
                    'hrv_rmssd_milli': score.get('hrv_rmssd_milli'),
                    'spo2_percentage': score.get('spo2_percentage'),
                    'skin_temp_celsius': score.get('skin_temp_celsius'),
                    'created_at': parse_datetime(item['created_at']),
                    'updated_at': parse_datetime(item['updated_at']),
                    'is_cutting_weight': profile.is_weight_cutting,
                }
            )
            synced_recoveries.append(recovery)

        # 5. Return from DB (ordered by cycle_id desc)
        serializer = RecoverySerializer(synced_recoveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
