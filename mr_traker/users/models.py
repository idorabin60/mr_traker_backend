import random
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    IS_TRAINER = 'TRAINER'
    IS_ATHLETE = 'ATHLETE'
    ROLE_CHOICES = [(IS_TRAINER, 'Trainer'), (IS_ATHLETE, 'Athlete')]

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=IS_ATHLETE)

    def __str__(self):
        return self.username


def generate_pass_key():
    return f"{random.randint(0, 999999):06d}"


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='trainer_profile')
    organization_name = models.CharField(max_length=100, blank=True, null=True)

    pass_key = models.CharField(
        max_length=6,
        unique=True,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        # Only generate on create or if missing
        if not self.pass_key:
            while True:
                candidate = generate_pass_key()
                if not TrainerProfile.objects.filter(pass_key=candidate).exists():
                    self.pass_key = candidate
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"TrainerProfile({self.user.username}, pass_key={self.pass_key})"


class AthleteProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='athlete_profile')
    trainers = models.ManyToManyField(
        User,
        blank=True,
        related_name='athletes',
        limit_choices_to={'role': User.IS_TRAINER},
    )
    #is werll conditopnd

    # What fields do i need to add here? : ask geminai
    is_weight_cutting = models.BooleanField(default=False)
    whoop_user_id = models.CharField(max_length=50, blank=True, null=True)

    # The short-lived key (valid for 1 hour)
    whoop_access_token = models.TextField(blank=True, null=True)

    # The long-lived key (valid strictly for getting new access tokens)
    whoop_refresh_token = models.TextField(blank=True, null=True)

    # We need to know WHEN to refresh
    whoop_token_expires_at = models.DateTimeField(blank=True, null=True)

# --- NEW MODEL: INVITE CODES ---
