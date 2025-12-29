from django.test import TestCase
from django.utils import timezone
from users.models import User, AthleteProfile
from sleep.models import Sleep
from sleep.serializers import SleepSerializer
import uuid

class SleepTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='athlete', password='password', role=User.IS_ATHLETE)
        self.athlete_profile = AthleteProfile.objects.create(user=self.user)
        
    def test_create_sleep(self):
        sleep_data = {
            "athlete": self.athlete_profile,
            "whoop_id": str(uuid.uuid4()),
            "whoop_user_id": 12345,
            "cycle_id": 67890,
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "start": timezone.now(),
            "end": timezone.now(),
            "timezone_offset": "-05:00",
            "nap": False,
            "score_state": "SCORED",
            "score": {"stage_summary": {}, "sleep_needed": {}, "respiratory_rate": 16.5}
        }
        
        sleep = Sleep.objects.create(**sleep_data)
        self.assertEqual(Sleep.objects.count(), 1)
        self.assertEqual(sleep.whoop_user_id, 12345)
        self.assertEqual(sleep.score['respiratory_rate'], 16.5)

    def test_serializer(self):
        sleep_data = {
            "athlete": self.athlete_profile,
            "whoop_id": str(uuid.uuid4()),
            "whoop_user_id": 12345,
            "cycle_id": 67890,
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "start": timezone.now(),
            "end": timezone.now(),
            "timezone_offset": "-05:00",
            "nap": False,
            "score_state": "SCORED",
            "score": {"stage_summary": {}, "sleep_needed": {}, "respiratory_rate": 16.5}
        }
        sleep = Sleep.objects.create(**sleep_data)
        serializer = SleepSerializer(sleep)
        data = serializer.data
        self.assertEqual(data['whoop_user_id'], 12345)
        self.assertEqual(data['score']['respiratory_rate'], 16.5)
