from rest_framework import serializers
from .models import Recovery

class RecoverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recovery
        fields = '__all__'
