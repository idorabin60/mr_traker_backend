from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date
from users.models import User, AthleteProfile
from recovery.models import Recovery
from sleep.models import Sleep
from workouts.models import Workout
from daily.models import Day
from daily.services import create_day_summary

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

class DayServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testservice', password='password')
        self.profile = AthleteProfile.objects.create(
            user=self.user,
            is_weight_cutting=True,
            is_preparing_for_competition=False,
            is_in_training_camp=True
        )
        self.today = timezone.now().date()
        self.today_datetime = timezone.now()

    def test_create_day_summary_aggregates_correctly(self):
        # 1. Create Data
        # Recovery
        Recovery.objects.create(
            athlete=self.profile,
            cycle_id=101,
            score_state='SCORED',
            recovery_score=85,
            created_at=self.today_datetime,
            updated_at=self.today_datetime
        )
        # Sleep
        Sleep.objects.create(
            athlete=self.profile,
            whoop_id='sleep1',
            whoop_user_id=123,
            cycle_id=101,
            created_at=self.today_datetime,
            updated_at=self.today_datetime,
            start=self.today_datetime - timedelta(hours=8),
            end=self.today_datetime, # Ends today
            timezone_offset='+00:00',
            score_state='SCORED',
            score={'sleep_efficiency_percentage': 92.5}
        )
        # Workout
        w = Workout.objects.create(
            athlete=self.profile,
            whoop_id='workout1',
            start=self.today_datetime, # Starts today
            end=self.today_datetime + timedelta(hours=1)
        )

        # Cycle (for Strain)
        from cycles.models import Cycle
        Cycle.objects.create(
            athlete=self.profile,
            whoop_id=101,
            whoop_user_id=123,
            created_at=self.today_datetime,
            updated_at=self.today_datetime,
            start=self.today_datetime,
            timezone_offset='+00:00',
            score_state='SCORED',
            score={'strain': 14.5}
        )

        # 2. Call Service
        day = create_day_summary(self.profile, self.today)

        # 3. Assertions
        self.assertEqual(day.athlete, self.profile)
        self.assertEqual(day.date, self.today)
        self.assertEqual(day.recovery_score, 85)
        self.assertEqual(day.sleep_efficient_score, 92) # Int conversion
        self.assertEqual(day.strain_score, 14.5)
        
        # Flags
        self.assertTrue(day.is_cutting_weight)
        self.assertFalse(day.is_preparing_for_competition)
        self.assertTrue(day.is_in_training_camp)

        # Signal Linking Check
        w.refresh_from_db()
        self.assertEqual(w.day, day)
