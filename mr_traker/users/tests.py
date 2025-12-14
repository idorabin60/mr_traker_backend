from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import requests

class WhoopIntegrationTests(TestCase):
    def test_privacy_policy_view(self):
        url = reverse('privacy-policy')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Privacy Policy")

    @patch('utils.whoop_service.requests.post')
    def test_whoop_callback_view_success(self, mock_post):
        # Mock successful token exchange
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_access_token",
            "refresh_token": "fake_refresh_token",
            "expires_in": 3600
        }

        url = reverse('whoop-callback')
        # Simulate redirect with code
        response = self.client.get(url, {'code': 'fake_oauth_code'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['token_data']['access_token'], 'fake_access_token')

    @patch('utils.whoop_service.requests.post')
    def test_whoop_callback_view_failure(self, mock_post):
        # Mock failed token exchange
        mock_response = mock_post.return_value
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Bad Request")

        url = reverse('whoop-callback')
        response = self.client.get(url, {'code': 'bad_code'})
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
