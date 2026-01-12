from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User, AthleteProfile
from rest_framework import status

class CycleSyncTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='password')
        self.profile = AthleteProfile.objects.create(user=self.user, whoop_access_token='fake_token')
        self.client.force_authenticate(user=self.user)
        
    @patch('cycles.views.requests.get')
    # Mocking get_valid_access_token from where it is imported in views.py
    @patch('cycles.views.get_valid_access_token')
    def test_cycle_sync(self, mock_get_token, mock_requests_get):
        mock_get_token.return_value = 'valid_token'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 93845,
                "user_id": 10129,
                "created_at": "2022-04-24T11:25:44.774Z",
                "updated_at": "2022-04-24T14:25:44.774Z",
                "start": "2022-04-24T02:25:44.774Z",
                "end": "2022-04-24T10:25:44.774Z",
                "timezone_offset": "-05:00",
                "score_state": "SCORED",
                "score": {"strain": 5.5, "kilojoule": 8000, "average_heart_rate": 70, "max_heart_rate": 150}
            }
        ]
        mock_requests_get.return_value = mock_response
        
        url = reverse('cycle-list') 
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['whoop_id'], 93845)
