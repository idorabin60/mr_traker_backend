from django.test import TestCase
from users.models import User, AthleteProfile
from daily.models import Day
from workouts.models import Workout
from datetime import date, datetime
from django.utils import timezone

class DayModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_day', password='password')
        self.profile = AthleteProfile.objects.create(
            user=self.user, 
            is_weight_cutting=True,
            is_preparing_for_competition=False,
            is_in_training_camp=True
        )

    def test_day_creation(self):
        today = date.today()
        day = Day.objects.create(
            athlete=self.profile,
            date=today,
            is_cutting_weight=self.profile.is_weight_cutting,
            is_preparing_for_competition=self.profile.is_preparing_for_competition,
            is_in_training_camp=self.profile.is_in_training_camp,
            recovery_score=85
        )
        
        self.assertTrue(day.is_cutting_weight)
        self.assertFalse(day.is_preparing_for_competition)
        self.assertTrue(day.is_in_training_camp)
        self.assertEqual(day.recovery_score, 85)

    def test_workout_auto_linking(self):
        # 1. Create a Workout for "today" (unlinked)
        now = timezone.now()
        workout = Workout.objects.create(
            athlete=self.profile,
            whoop_id="wk_123",
            start=now,
            end=now,
            strain=10.0
        )
        
        # Verify it has no Day yet
        self.assertIsNone(workout.day)
        
        # 2. Create the Day for "today"
        today = now.date()
        day = Day.objects.create(
            athlete=self.profile,
            date=today
        )
        
        # 3. Refresh workout and check link
        workout.refresh_from_db()
        self.assertEqual(workout.day, day)
