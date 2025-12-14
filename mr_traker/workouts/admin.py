from django.contrib import admin
from .models import Workout

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'athlete', 'start', 'end', 'score_state', 'strain', 'average_heart_rate', 'max_heart_rate', 'kilojoule', 'percent_recorded', 'distance_meter', 'altitude_gain_meter', 'altitude_change_meter', 'whoop_id', 'sport_id', 'created_at')
    list_filter = ('score_state', 'athlete', 'start')
    search_fields = ('whoop_id', 'athlete__user__username')
    ordering = ('-start',)
