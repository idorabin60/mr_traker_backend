from django.contrib import admin
from .models import Recovery

@admin.register(Recovery)
class RecoveryAdmin(admin.ModelAdmin):
    list_display = (
        'cycle_id', 'athlete', 'recovery_score', 'resting_heart_rate', 
        'hrv_rmssd_milli', 'spo2_percentage', 'skin_temp_celsius', 
        'score_state', 'user_calibrating', 'sleep_id', 'created_at', 'updated_at'
    )
    list_filter = ('score_state', 'athlete')
    search_fields = ('cycle_id', 'athlete__user__username')
    ordering = ('-cycle_id',)
