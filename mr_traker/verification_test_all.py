from django.test import TestCase
from django.utils import timezone
from users.models import User, AthleteProfile
from workouts.models import Workout
from recovery.models import Recovery
import json

class WeightCuttingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testathlete', role=User.IS_ATHLETE)
        self.profile = AthleteProfile.objects.create(user=self.user, is_weight_cutting=True)

    def test_workout_creation(self):
        workout = Workout.objects.create(
            athlete=self.profile,
            whoop_id='w1',
            start=timezone.now(),
            end=timezone.now(),
            is_cutting_weight=self.profile.is_weight_cutting
        )
        self.assertTrue(workout.is_cutting_weight)

        self.profile.is_weight_cutting = False
        self.profile.save()
        
        workout2 = Workout.objects.create(
            athlete=self.profile,
            whoop_id='w2',
            start=timezone.now(),
            end=timezone.now(),
            is_cutting_weight=self.profile.is_weight_cutting
        )
        self.assertFalse(workout2.is_cutting_weight)

    def test_recovery_creation(self):
        recovery = Recovery.objects.create(
            athlete=self.profile,
            cycle_id=101,
            score_state='complete',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_cutting_weight=self.profile.is_weight_cutting
        )
        self.assertTrue(recovery.is_cutting_weight)

        self.profile.is_weight_cutting = False
        self.profile.save()

        recovery2 = Recovery.objects.create(
            athlete=self.profile,
            cycle_id=102,
            score_state='complete',
            created_at=timezone.now(),
            updated_at=timezone.now(),
            is_cutting_weight=self.profile.is_weight_cutting
        )
        self.assertFalse(recovery2.is_cutting_weight)
