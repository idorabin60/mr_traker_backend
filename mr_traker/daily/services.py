from django.utils import timezone
from .models import Day
from recovery.models import Recovery
from sleep.models import Sleep

def create_day_summary(athlete_profile, date=None):
    """
    Creates or updates a Day object for the given athlete and date.
    Aggregates data from Recovery, Sleep, and AthleteProfile.
    """
    if date is None:
        date = timezone.now().date()

    # 1. Fetch Recovery Data
    # Recovery for a day is usually associated with the sleep ending on that day.
    # We look for a recovery record created on this date.
    # Note: Adjust logic if Recovery.created_at isn't the best field, 
    # but typically 'recovery' is generated in the morning of 'date'.
    recovery_qs = Recovery.objects.filter(
        athlete=athlete_profile,
        created_at__date=date
    ).order_by('-created_at') # Get latest if multiple?
    
    recovery_obj = recovery_qs.first()
    recovery_score = recovery_obj.recovery_score if recovery_obj else None

    # 2. Fetch Sleep Data
    # Sleep ending on 'date' is usually the sleep for that 'day'.
    # e.g., Sleep ending 2024-01-01 07:00 AM belongs to Day 2024-01-01.
    sleep_qs = Sleep.objects.filter(
        athlete=athlete_profile,
        end__date=date
    ).order_by('-end')
    
    sleep_obj = sleep_qs.first()
    sleep_efficient_score = None
    if sleep_obj and sleep_obj.score:
        # Assuming score structure based on previous logs/models
        # score -> sleep_efficiency_percentage
        sleep_efficient_score = sleep_obj.score.get('sleep_efficiency_percentage')
        # If it's a float like 95.0, cast to int? Model says IntegerField.
        if sleep_efficient_score is not None:
             sleep_efficient_score = int(float(sleep_efficient_score))

    # 3. Create or Update Day
    day, created = Day.objects.update_or_create(
        athlete=athlete_profile,
        date=date,
        defaults={
            'recovery_score': recovery_score,
            'sleep_efficient_score': sleep_efficient_score,
            # 'strain_score': ??? (Not specified in source, maybe calculated from workouts?)
            
            # Flags from Profile
            'is_cutting_weight': athlete_profile.is_weight_cutting,
            'is_preparing_for_competition': athlete_profile.is_preparing_for_competition,
            'is_in_training_camp': athlete_profile.is_in_training_camp,
        }
    )
    
    return day
