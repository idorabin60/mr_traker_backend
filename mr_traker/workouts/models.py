from django.db import models
from users.models import AthleteProfile

class Workout(models.Model):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='workouts')
    day = models.ForeignKey('daily.Day', on_delete=models.SET_NULL, null=True, blank=True, related_name='workouts')
    whoop_id = models.CharField(max_length=50, unique=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    timezone_offset = models.CharField(max_length=10, blank=True, null=True)
    sport_id = models.IntegerField(blank=True, null=True)
    score_state = models.CharField(max_length=20, blank=True, null=True)
    
    # Measurements (from 'score' object)
    strain = models.FloatField(blank=True, null=True)
    average_heart_rate = models.IntegerField(blank=True, null=True)
    max_heart_rate = models.IntegerField(blank=True, null=True)
    kilojoule = models.FloatField(blank=True, null=True)
    percent_recorded = models.FloatField(blank=True, null=True)
    distance_meter = models.FloatField(blank=True, null=True)
    altitude_gain_meter = models.FloatField(blank=True, null=True)
    altitude_change_meter = models.FloatField(blank=True, null=True)
    
    is_cutting_weight = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workout {self.whoop_id} - {self.start}"
