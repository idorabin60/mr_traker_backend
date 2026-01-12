from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User, AthleteProfile
from rest_framework import status
import hmac
import hashlib
import base64
import json

class WebhookCycleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_hook', password='password')
        # Use simple ID for whoop_user_id to match test data
        self.profile = AthleteProfile.objects.create(user=self.user, whoop_access_token='fake_token', whoop_user_id='10129')
        # Ensure client secret is set for signing
        from django.conf import settings
        self.secret = getattr(settings, 'WHOOP_CLIENT_SECRET', 'test_secret')

    @patch('users.views.whoop_service.get_cycle_by_id')
    @patch('users.views.whoop_service.get_recovery_by_cycle_id')
    @patch('users.views.whoop_service.get_valid_access_token')
    def test_webhook_triggers_cycle_sync(self, mock_get_token, mock_get_recovery, mock_get_cycle):
        mock_get_token.return_value = 'valid_token'
        
        # Mock Recovery Data
        mock_get_recovery.return_value = {
            "cycle_id": 93845,
            "sleep_id": "sleep-uuid-123",
            "score_state": "SCORED",
            "created_at": "2022-04-24T12:00:00Z",
            "updated_at": "2022-04-24T12:00:00Z",
            "score": {"recovery_score": 90}
        }
        
        # Mock Cycle Data
        mock_get_cycle.return_value = {
            "id": 93845,
            "user_id": 10129,
            "created_at": "2022-04-24T11:25:44.774Z",
            "updated_at": "2022-04-24T14:25:44.774Z",
            "start": "2022-04-24T02:25:44.774Z",
            "end": "2022-04-24T10:25:44.774Z",
            "timezone_offset": "-05:00",
            "score_state": "SCORED",
            "score": {"strain": 5.5}
        }

        # Payload
        payload = {
            "type": "recovery.updated",
            "user_id": 10129,
            "id": 93845, # Cycle ID in this case
            "trace_id": "abc"
        }
        payload_bytes = json.dumps(payload).encode('utf-8')
        timestamp = "1234567890"
        
        # Sign Payload
        to_sign = timestamp.encode('utf-8') + payload_bytes
        signature = base64.b64encode(hmac.new(
            key=self.secret.encode('utf-8'),
            msg=to_sign,
            digestmod=hashlib.sha256
        ).digest()).decode('utf-8')

        headers = {
            'HTTP_X_WHOOP_SIGNATURE': signature,
            'HTTP_X_WHOOP_SIGNATURE_TIMESTAMP': timestamp
        }

        url = reverse('whoop-webhook')
        response = self.client.post(url, payload, content_type='application/json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify Cycle was created
        from cycles.models import Cycle
        self.assertTrue(Cycle.objects.filter(whoop_id=93845).exists())
        cycle = Cycle.objects.get(whoop_id=93845)
        self.assertEqual(cycle.score['strain'], 5.5)
