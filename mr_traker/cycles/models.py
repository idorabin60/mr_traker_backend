from django.db import models
from users.models import AthleteProfile

class Cycle(models.Model):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='cycles')
    whoop_id = models.IntegerField(unique=True, help_text="Unique identifier for the cycle activity")
    whoop_user_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    timezone_offset = models.CharField(max_length=10)
    score_state = models.CharField(max_length=20)
    score = models.JSONField(help_text="Nested score object from Whoop API")

    def __str__(self):
        return f"Cycle {self.whoop_id} for {self.athlete.user.username}"
