from rest_framework import serializers
from .models import MedicalHistory, MedicalHistoryNote

class MedicalHistoryNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistoryNote
        fields = ['id', 'role', 'date', 'description']

class MedicalHistorySerializer(serializers.ModelSerializer):
    notes = MedicalHistoryNoteSerializer(many=True, read_only=True)

    class Meta:
        model = MedicalHistory
        fields = ['id', 'athlete', 'title', 'description', 'created_at', 'notes']
        read_only_fields = ['created_at']
