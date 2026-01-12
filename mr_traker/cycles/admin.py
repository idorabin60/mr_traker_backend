from django.contrib import admin
from .models import Cycle

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ('whoop_id', 'athlete', 'start', 'end', 'score_state', 'created_at')
    search_fields = ('whoop_id', 'athlete__user__username', 'score_state')
    list_filter = ('score_state', 'created_at')
