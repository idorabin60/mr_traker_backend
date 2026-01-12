from django.contrib import admin
from .models import Day

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ('date', 'athlete', 'recovery_score', 'strain_score', 'is_cutting_weight')
    list_filter = ('is_cutting_weight', 'is_preparing_for_competition', 'is_in_training_camp')
