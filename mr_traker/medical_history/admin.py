from django.contrib import admin
from .models import MedicalHistory, MedicalHistoryNote

class MedicalHistoryNoteInline(admin.TabularInline):
    model = MedicalHistoryNote
    extra = 1

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'athlete', 'created_at')
    search_fields = ('title', 'athlete__user__username')
    inlines = [MedicalHistoryNoteInline]

@admin.register(MedicalHistoryNote)
class MedicalHistoryNoteAdmin(admin.ModelAdmin):
    list_display = ('medical_history', 'role', 'date', 'description')
    list_filter = ('role', 'date')
    search_fields = ('medical_history__title', 'description')
