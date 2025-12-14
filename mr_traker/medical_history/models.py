from django.db import models
from django.utils import timezone
from users.models import AthleteProfile

class MedicalHistory(models.Model):
    athlete = models.ForeignKey(
        AthleteProfile,
        on_delete=models.CASCADE,
        related_name='medical_histories'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    # notes field removed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.athlete})"

class MedicalHistoryNote(models.Model):
    ROLE_CHOICES = [
        ('AI', 'AI'),
        ('HUMAN', 'Human'),
    ]
    
    medical_history = models.ForeignKey(
        MedicalHistory,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField()
    
    def __str__(self):
        return f"Note by {self.role} on {self.date}"
