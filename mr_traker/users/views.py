from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

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
