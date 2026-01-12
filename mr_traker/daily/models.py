from django.db import models
from users.models import AthleteProfile


class Day(models.Model):
    athlete = models.ForeignKey(AthleteProfile, on_delete=models.CASCADE, related_name='days')
    date = models.DateField(help_text="The date this summary represents")
    
    # Metrics
    recovery_score = models.IntegerField(blank=True, null=True)
    sleep_efficient_score = models.IntegerField(blank=True, null=True)
    strain_score = models.FloatField(blank=True, null=True)
    
    # Relationships
    
    # Status Flags
    is_cutting_weight = models.BooleanField(default=False)
    is_preparing_for_competition = models.BooleanField(default=False)
    is_in_training_camp = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('athlete', 'date')

    def __str__(self):
        return f"Day {self.date} for {self.athlete.user.username}"
