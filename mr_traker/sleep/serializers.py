from rest_framework import serializers
from .models import Sleep

class SleepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sleep
        fields = '__all__'
