from rest_framework import serializers
from .models import Day
from sleep.models import Sleep
from recovery.models import Recovery
from recovery.serializers import RecoverySerializer

class DaySerializer(serializers.ModelSerializer):
    sleep_details = serializers.SerializerMethodField()
    recovery_details = serializers.SerializerMethodField()

    class Meta:
        model = Day
        fields = (
            'id', 
            'date', 
            'recovery_score', 
            'sleep_efficient_score', 
            'strain_score',
            'is_cutting_weight', 
            'is_preparing_for_competition', 
            'is_in_training_camp',
            'sleep_details',
            'recovery_details'
        )

    def get_sleep_details(self, obj):
        # Fetch the sleep object for this day (usually ending on this day)
        # We use the same logic as created in create_day_summary
        sleep_obj = Sleep.objects.filter(
            athlete=obj.athlete,
            end__date=obj.date
        ).order_by('-end').first()
        
        if sleep_obj and sleep_obj.score:
            # The frontend expects the nested score object directly
            return sleep_obj.score
        return None

    def get_recovery_details(self, obj):
        # Fetch recovery object created on this day
        recovery_obj = Recovery.objects.filter(
            athlete=obj.athlete,
            created_at__date=obj.date
        ).order_by('-created_at').first()
        
        if recovery_obj:
            return RecoverySerializer(recovery_obj).data
        return None
