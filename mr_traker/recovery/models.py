from django.db import models
from users.models import AthleteProfile

class Recovery(models.Model):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='recoveries')
    cycle_id = models.IntegerField(unique=True)
    sleep_id = models.CharField(max_length=50, blank=True, null=True)
    score_state = models.CharField(max_length=50)
    
    # Score details
    user_calibrating = models.BooleanField(default=False)
    recovery_score = models.IntegerField(blank=True, null=True)
    resting_heart_rate = models.IntegerField(blank=True, null=True)
    hrv_rmssd_milli = models.FloatField(blank=True, null=True)
    spo2_percentage = models.FloatField(blank=True, null=True)
    skin_temp_celsius = models.FloatField(blank=True, null=True)
    
    created_at = models.DateTimeField() # From WHOOP API
    updated_at = models.DateTimeField() # From WHOOP API

    def __str__(self):
        return f"Recovery {self.recovery_score}% (Cycle {self.cycle_id})"
