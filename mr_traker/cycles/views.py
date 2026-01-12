from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.dateparse import parse_datetime
import requests

from .models import Cycle
from .serializers import CycleSerializer
from utils.whoop_service import get_valid_access_token

class CycleListView(APIView):
    """
    GET /api/cycles/
    Fetches latest cycle data from WHOOP and returns them.
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
        # Using V1 for Cycle Collection as per standard Whoop API patterns
        limit = request.query_params.get('limit', 25)
        url = f"https://api.prod.whoop.com/developer/v1/cycle?limit={limit}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
             
            # Paginated response? V1 usually returns a list or wrapper? 
            # If it's like V2 sleep, it might be wrapped. 
            # But standard V1 often returns list. I'll handle both.
            # Docs say "Get all ... paginated". Usually keys are 'records' or just list.
            if isinstance(data, dict) and 'records' in data:
                 data = data['records']
            elif isinstance(data, list):
                # direct list
                pass

        except requests.exceptions.RequestException as e:
            return Response({"detail": f"Failed to fetch cycles from WHOOP: {e}"}, status=status.HTTP_502_BAD_GATEWAY)

        # 4. Sync to DB
        synced_cycles = []
        for item in data:
            score = item.get('score', {})
            
            # Use whoop_id (the API 'id') as the unique identifier
            cycle_obj, created = Cycle.objects.update_or_create(
                whoop_id=item['id'],
                defaults={
                    'athlete': profile,
                    'whoop_user_id': item['user_id'],
                    'created_at': parse_datetime(item['created_at']),
                    'updated_at': parse_datetime(item['updated_at']),
                    'start': parse_datetime(item['start']),
                    'end': parse_datetime(item['end']) if item.get('end') else None,
                    'timezone_offset': item['timezone_offset'],
                    'score_state': item['score_state'],
                    'score': score,
                }
            )
            synced_cycles.append(cycle_obj)

        # 5. Return from DB
        serializer = CycleSerializer(synced_cycles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
