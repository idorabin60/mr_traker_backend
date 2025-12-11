from rest_framework import serializers
from django.db import transaction
from .models import User, TrainerProfile, AthleteProfile


class TrainerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerProfile
        fields = ("organization_name", "pass_key")
        read_only_fields = ("pass_key",)


class AthleteProfileSerializer(serializers.ModelSerializer):
    trainers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.filter(role=User.IS_TRAINER),
        required=False,
    )

    class Meta:
        model = AthleteProfile
        fields = (
            "trainers",
            "whoop_user_id",
            "whoop_access_token",
            "whoop_refresh_token",
            "whoop_token_expires_at",
        )
        extra_kwargs = {
            "whoop_access_token": {"write_only": True},
            "whoop_refresh_token": {"write_only": True},
        }


class UserSerializer(serializers.ModelSerializer):
    trainer_profile = TrainerProfileSerializer(read_only=True)
    athlete_profile = AthleteProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "trainer_profile",
            "athlete_profile",
        )
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Used for signup. Creates:
      - User
      - TrainerProfile if role == TRAINER
      - AthleteProfile if role == ATHLETE
    """
    password = serializers.CharField(write_only=True)
    trainer_pass_key = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    organization_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "role", "organization_name")

    def validate_role(self, value):
        if value not in (User.IS_TRAINER, User.IS_ATHLETE):
            raise serializers.ValidationError(
                "Role must be TRAINER or ATHLETE.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        org_name = validated_data.pop("organization_name", "")
        trainer_pass_key = validated_data.pop("trainer_pass_key", "").strip()
        password = validated_data.pop("password")
        role = validated_data.get("role", User.IS_ATHLETE)

        # 1. Create the User
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=password,
            role=role,
        )

        # 2. Create the correct profile
        if role == User.IS_TRAINER:
            TrainerProfile.objects.create(
                user=user, organization_name=org_name)
        else:
            athlete_profile = AthleteProfile.objects.create(user=user)
            # If athlete sent a trainer_pass_key → link them to that trainer
            if trainer_pass_key:
                try:
                    trainer_profile = TrainerProfile.objects.get(
                        pass_key=trainer_pass_key)
                except TrainerProfile.DoesNotExist:
                    # Rollback everything (because of @transaction.atomic)
                    raise serializers.ValidationError({
                        "trainer_pass_key": "Invalid trainer_pass_key."
                    })

                # Link athlete to this trainer
                athlete_profile.trainers.add(trainer_profile.user)

        return user
