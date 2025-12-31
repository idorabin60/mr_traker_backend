from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import HttpResponse
from utils import whoop_service


from .serializers import RegisterSerializer, UserSerializer
from .models import User


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Body:
    {
      "username": "coach_avi",
      "email": "avi@example.com",
      "password": "12345678",
      "role": "TRAINER",  # or "ATHLETE"
      "organization_name": "Avi Gym"   # only relevant for trainers
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Body:
    {
      "username": "coach_avi",
      "password": "12345678"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
            },
            status=status.HTTP_200_OK,
        )


class MyAthletesView(APIView):
    """
    GET /api/trainer/athletes/
    Returns all athlete users that are linked to the CURRENT logged-in trainer.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trainer = request.user

        # Only trainers should use this endpoint
        if trainer.role != User.IS_TRAINER:
            return Response(
                {"detail": "Only trainers can view their athletes."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get all Users that have an AthleteProfile and are linked to this trainer
        athletes_qs = User.objects.filter(
            athlete_profile__trainers=trainer
        ).select_related("athlete_profile")

        serializer = UserSerializer(athletes_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PrivacyPolicyView(APIView):
    """
    GET /api/users/privacy-policy/
    Simple endpoint to display privacy policy.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return HttpResponse("<h1>Privacy Policy</h1><p>This is a placeholder privacy policy for Whoop integration.</p>")


class WhoopCallbackView(APIView):
    """
    GET /api/users/whoop/callback/
    Handles the redirect from WHOOP after user authorizes the app.
    Query Params: ?code=...&state=...
    """
    permission_classes = [permissions.AllowAny]  # Or IsAuthenticated if you want to link to logged-in user

    def get(self, request):
        print(request)
        code = request.query_params.get("code")
        error = request.query_params.get("error")

        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if not code:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange code for token
        token_data = whoop_service.exchange_oauth_code(code)
        print("LOOK HERE IDO:")
        print(token_data)

        if not token_data:
            return Response({"error": "Failed to exchange code for token"}, status=status.HTTP_400_BAD_REQUEST)

        # ------------------------------------------------------------------
        # PROVISIONAL LOGIC: HARDCODED LINKING
        # ------------------------------------------------------------------
        from django.utils import timezone
        from datetime import timedelta
        from .models import User, AthleteProfile, TrainerProfile

        # 1. Get or Create the specific user
        try:
            user, created = User.objects.get_or_create(
                username="idorabin60",
                defaults={"email": "idorabin60@example.com", "role": User.IS_ATHLETE}
            )
            if created:
                user.set_password("password123") # Set a default password if created
                user.save()
        except Exception as e:
             return Response({"error": f"Error getting user: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Get or Create AthleteProfile
        athlete_profile, _ = AthleteProfile.objects.get_or_create(user=user)

        # 3. Store Tokens
        # Fetch User Profile to get user_id FIRST
        user_profile = whoop_service.get_user_profile(token_data['access_token'])
        print(f"User Profile Fetched: {user_profile}")
        
        if user_profile and 'user_id' in user_profile:
            athlete_profile.whoop_user_id = user_profile['user_id']
        elif 'user_id' in token_data:
             # Fallback if it WAS in token_data, though user says it isn't
             athlete_profile.whoop_user_id = token_data['user_id']
        
        athlete_profile.whoop_access_token = token_data['access_token']
        athlete_profile.whoop_refresh_token = token_data['refresh_token']
        
        expires_in = token_data.get('expires_in', 3600)
        athlete_profile.whoop_token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        athlete_profile.save()

        # 4. Link to Trainer 12345
        trainer_linked = False
        try:
            trainer_profile = TrainerProfile.objects.get(pass_key="12345")
            athlete_profile.trainers.add(trainer_profile.user)
            trainer_linked = True
        except TrainerProfile.DoesNotExist:
            print("Trainer with passkey 12345 not found.")

        return Response({
            "message": "WHOOP connected and linked successfully!",
            "linked_user": user.username,
            "trainer_linked": trainer_linked,
            "token_data": token_data 
        }, status=status.HTTP_200_OK)


class WhoopWebhookView(APIView):
    """
    POST /api/users/whoop/webhook/
    Standard webhook endpoint for Whoop notifications.
    Verifies signature and prints data.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import hmac
        import hashlib
        import base64
        from django.conf import settings
        print("LOOK HERE IDO:")
        print(request)

        # 1. Get headers
        signature = request.headers.get("X-WHOOP-Signature")
        timestamp = request.headers.get("X-WHOOP-Signature-Timestamp")

        if not signature or not timestamp:
            return Response(
                {"detail": "Missing X-WHOOP-Signature or X-WHOOP-Signature-Timestamp"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Verify Signature
        # Formula: base64Encode(HMACSHA256(timestamp_header + raw_http_request_body, client_secret))
        
        # Ensure we have the raw body bytes. 
        # DRF might have read it already, but request.body should still be accessible if not consumed by a stream.
        # If this fails in future execution, we might need to handle body buffering.
        raw_body = request.body 
        
        secret = settings.WHOOP_CLIENT_SECRET
        if not secret:
            print("ERROR: WHOOP_CLIENT_SECRET is not set in settings/env")
            return Response({"detail": "Server misconfiguration"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Prepare the data to sign
        # timestamp is a string, raw_body is bytes. We need to concatenate them as bytes.
        payload_to_sign = timestamp.encode('utf-8') + raw_body
        
        # Calculate HMAC
        calculated_hmac = hmac.new(
            key=secret.encode('utf-8'),
            msg=payload_to_sign,
            digestmod=hashlib.sha256
        ).digest()
        
        calculated_signature = base64.b64encode(calculated_hmac).decode('utf-8')

        # Compare constant time
        if not hmac.compare_digest(calculated_signature, signature):
            print(f"Signature mismatch! Calculated: {calculated_signature}, Received: {signature}")
            return Response({"detail": "Invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        # 3. Process Data
        print("Received verified Whoop Webhook:")
        print(request.data)

        # Handle Workout Updates
        event_type = request.data.get('type')
        user_id = request.data.get('user_id')
        resource_id = request.data.get('id')

        if event_type in ['workout.updated', 'workout.created'] and user_id and resource_id:
            from .models import AthleteProfile
            from workouts.models import Workout
            from utils import whoop_service
            from django.utils.dateparse import parse_datetime

            # Find the athlete
            # Note: whoop_user_id is stored as CharField/Integer? Models say CharField in sleep/models but check users/models
            # In users/models.py it is CharField. API returns int usually. We should cast or filter loosely.
            try:
                profile = AthleteProfile.objects.get(whoop_user_id=str(user_id))
            except AthleteProfile.DoesNotExist:
                print(f"Webhook received for unknown user_id: {user_id}")
                return Response({"status": "unknown_user"}, status=status.HTTP_200_OK)

            # Get fresh token
            access_token = whoop_service.get_valid_access_token(profile)
            if not access_token:
                print(f"Could not get valid token for user {user_id}")
                return Response({"status": "token_error"}, status=status.HTTP_200_OK)

            # Fetch Workout Details
            workout_data = whoop_service.get_workout_by_id(access_token, resource_id)
            if workout_data:
                print("WORKOUT DATA::")
                print(workout_data)
                print(f"Syncing workout {resource_id} for user {user_id}")
                score = workout_data.get('score', {})
                
                Workout.objects.update_or_create(
                    whoop_id=workout_data['id'],
                    defaults={
                        'athlete': profile,
                        'start': parse_datetime(workout_data['start']),
                        'end': parse_datetime(workout_data['end']),
                        'timezone_offset': workout_data.get('timezone_offset'),
                        'sport_id': workout_data.get('sport_id'),
                        'score_state': workout_data.get('score_state'),
                        # Score fields
                        'strain': score.get('strain'),
                        'average_heart_rate': score.get('average_heart_rate'),
                        'max_heart_rate': score.get('max_heart_rate'),
                        'kilojoule': score.get('kilojoule'),
                        'percent_recorded': score.get('percent_recorded'),
                        'distance_meter': score.get('distance_meter'),
                        'altitude_gain_meter': score.get('altitude_gain_meter'),
                        'altitude_change_meter': score.get('altitude_change_meter'),
                        'is_cutting_weight': profile.is_weight_cutting,
                    }
                )
            else:
                print(f"Failed to fetch workout data for {resource_id}")

        elif event_type in ['sleep.updated', 'sleep.created'] and user_id and resource_id:
            from .models import AthleteProfile
            from sleep.models import Sleep
            from utils import whoop_service
            from django.utils.dateparse import parse_datetime

            try:
                profile = AthleteProfile.objects.get(whoop_user_id=str(user_id))
            except AthleteProfile.DoesNotExist:
                return Response({"status": "unknown_user"}, status=status.HTTP_200_OK)

            access_token = whoop_service.get_valid_access_token(profile)
            if not access_token:
                return Response({"status": "token_error"}, status=status.HTTP_200_OK)

            sleep_data = whoop_service.get_sleep_by_id(access_token, resource_id)
            if sleep_data:
                print(f"Syncing sleep {resource_id} for user {user_id}")
                score = sleep_data.get('score', {})
                Sleep.objects.update_or_create(
                    whoop_id=sleep_data['id'],
                    defaults={
                        'athlete': profile,
                        'whoop_user_id': sleep_data['user_id'],
                        'cycle_id': sleep_data['cycle_id'],
                        'created_at': parse_datetime(sleep_data['created_at']),
                        'updated_at': parse_datetime(sleep_data['updated_at']),
                        'start': parse_datetime(sleep_data['start']),
                        'end': parse_datetime(sleep_data['end']),
                        'timezone_offset': sleep_data['timezone_offset'],
                        'nap': sleep_data['nap'],
                        'score_state': sleep_data['score_state'],
                        'score': score,
                        'is_cutting_weight': profile.is_weight_cutting,
                    }
                )
            else:
                print(f"Failed to fetch sleep data for {resource_id}")

        elif event_type in ['recovery.updated', 'recovery.created'] and user_id and resource_id:
            from .models import AthleteProfile
            from recovery.models import Recovery
            from utils import whoop_service
            from django.utils.dateparse import parse_datetime

            try:
                profile = AthleteProfile.objects.get(whoop_user_id=str(user_id))
            except AthleteProfile.DoesNotExist:
                return Response({"status": "unknown_user"}, status=status.HTTP_200_OK)

            access_token = whoop_service.get_valid_access_token(profile)
            if not access_token:
                return Response({"status": "token_error"}, status=status.HTTP_200_OK)

            # Resolve Cycle ID
            # Webhook ID is likely Sleep UUID.
            resolved_cycle_id = None
            
            # Simple heuristic: if dashes, it's a UUID (Sleep ID). If digits only, Cycle ID.
            if '-' in str(resource_id):
                # Fetch Sleep to get Cycle ID
                sleep_data = whoop_service.get_sleep_by_id(access_token, resource_id)
                if sleep_data:
                    resolved_cycle_id = sleep_data.get('cycle_id')
                    print(f"Resolved Recovery Cycle ID {resolved_cycle_id} from Sleep ID {resource_id}")
            else:
                # Assume it is cycle ID
                resolved_cycle_id = resource_id

            if resolved_cycle_id:
                recovery_data = whoop_service.get_recovery_by_cycle_id(access_token, resolved_cycle_id)
                if recovery_data:
                    print(f"Syncing recovery for cycle {resolved_cycle_id}")
                    score = recovery_data.get('score', {})
                    Recovery.objects.update_or_create(
                        cycle_id=recovery_data['cycle_id'],
                        defaults={
                            'athlete': profile,
                            'sleep_id': recovery_data.get('sleep_id'),
                            'score_state': recovery_data.get('score_state'),
                            'user_calibrating': score.get('user_calibrating', False),
                            'recovery_score': score.get('recovery_score'),
                            'resting_heart_rate': score.get('resting_heart_rate'),
                            'hrv_rmssd_milli': score.get('hrv_rmssd_milli'),
                            'spo2_percentage': score.get('spo2_percentage'),
                            'skin_temp_celsius': score.get('skin_temp_celsius'),
                            'created_at': parse_datetime(recovery_data['created_at']),
                            'updated_at': parse_datetime(recovery_data['updated_at']),
                            'is_cutting_weight': profile.is_weight_cutting,
                        }
                    )
                else:
                    print(f"Failed to fetch recovery data for cycle {resolved_cycle_id}")
            else:
                print(f"Could not resolve cycle_id from resource {resource_id}")

        # Return 200 OK quickly
        return Response({"status": "received"}, status=status.HTTP_200_OK)
