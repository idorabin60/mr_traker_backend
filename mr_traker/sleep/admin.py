from django.contrib import admin
from .models import Sleep

@admin.register(Sleep)
class SleepAdmin(admin.ModelAdmin):
    list_display = ('id', 'athlete', 'start', 'score_state', 'created_at')
    list_filter = ('score_state', 'created_at')
    search_fields = ('athlete__user__username', 'whoop_id')
