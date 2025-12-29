from django.db import models
from users.models import AthleteProfile

class Sleep(models.Model):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='sleeps')
    whoop_id = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the sleep activity")
    whoop_user_id = models.IntegerField()
    cycle_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    timezone_offset = models.CharField(max_length=10)
    nap = models.BooleanField(default=False)
    score_state = models.CharField(max_length=20)
    score = models.JSONField(help_text="Nested score object from Whoop API")
    is_cutting_weight = models.BooleanField(default=False)

    def __str__(self):
        return f"Sleep {self.whoop_id} for {self.athlete.user.username}"
