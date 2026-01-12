from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Day
from workouts.models import Workout

@receiver(post_save, sender=Day)
def link_workouts_to_day(sender, instance, created, **kwargs):
    """
    When a Day is saved, find all workouts for that athlete and date
    that are not yet linked (or even if they are linked to another day day, 
    though typically we just want to ensure they are linked to THIS day).
    """
    
    # Filter workouts for the same athlete and date (using start date of workout)
    # Note: Workout.start is DateTimeField. We compare against the date part.
    workouts = Workout.objects.filter(
        athlete=instance.athlete,
        start__date=instance.date
    )
    
    # Update them to point to this Day instance
    workouts.update(day=instance)
