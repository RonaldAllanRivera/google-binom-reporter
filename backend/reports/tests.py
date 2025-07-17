import json
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from .models import GoogleAccount

# Helper to create a user with specific permissions
def create_test_user(username='testuser', password='password', email=None, is_staff=False, is_superuser=False, perms=None):
    user_email = email or f'{username}@example.com'
    user = User.objects.create_user(username=username, password=password, email=user_email)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    return user

class AuthAPITests(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.login(username=self.user.username, password='password')

    def test_user_status_view(self):
        url = reverse('user_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_logout_view(self):
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

@patch('reports.views.build_auth_url')
class GoogleAuthTests(APITestCase):
    def test_google_auth_url_view(self, mock_build_auth_url):
        mock_build_auth_url.return_value = 'https://auth.url/test'
        
        url = reverse('google_auth_url')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['auth_url'], 'https://auth.url/test')

    @patch('reports.views.exchange_code_for_tokens')
    @patch('reports.views.login')
    def test_google_auth_callback_view(self, mock_login, mock_exchange_tokens, mock_build_auth_url):
        # Setup mocks
        mock_exchange_tokens.return_value = {'user_email': 'newuser@google.com', 'refresh_token': 'fake_token'}

        url = reverse('google_auth_callback')
        response = self.client.get(url, {'code': 'test_code'})
        
        self.assertTrue(User.objects.filter(email='newuser@google.com').exists())
        self.assertEqual(mock_login.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND) # It redirects to frontend

@patch('reports.permissions.IsGoogleOrSuperuser.has_permission', return_value=True)
class ReportAPITests(APITestCase):
    def setUp(self):
        self.user = create_test_user(username='googleuser', email='googleuser@example.com')
        self.client.login(username=self.user.username, password='password')
        # Create a corresponding GoogleAccount for the user to prevent 404s
        GoogleAccount.objects.create(user_email=self.user.email, refresh_token='fake_token')

    @patch('reports.views.fetch_all_client_campaign_costs')
    def test_google_ads_test_view(self, mock_fetch_costs, mock_perm):
        mock_fetch_costs.return_value = {'test_cost': 'data'}
        
        url = reverse('google_ads_test')
        # Pass required params
        response = self.client.get(url, {'email': self.user.email, 'start_date': '2024-01-01', 'end_date': '2024-01-31'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'test_cost': 'data'})

    @patch('reports.views.fetch_binom_data')
    def test_generate_report_view(self, mock_fetch_binom, mock_perm):
        mock_fetch_binom.return_value = [{'name': 'Campaign A', 'revenue': '100', 'leads': '10'}]
        
        url = reverse('generate_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('reports.google_auth_service.get_all_accounts_in_hierarchy')
    def test_google_ads_manager_check_view(self, mock_get_accounts, mock_perm):
        mock_get_accounts.return_value = [{'account': 'details'}]

        url = reverse('google_ads_manager_check')
        response = self.client.get(url, {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('reports.views.fetch_all_client_campaign_costs')
    @patch('reports.views.fetch_binom_data')
    @patch('reports.google_ads_client.GoogleAdsClient')
    def test_combined_report_view(self, mock_google_ads_client, mock_fetch_binom, mock_fetch_costs, mock_perm):
        from django.conf import settings
        
        # Set up mock return values
        mock_fetch_binom.return_value = {'data': []}
        mock_fetch_costs.return_value = {'data': []}
        
        # Mock the Google Ads client
        mock_client_instance = mock_google_ads_client.load_from_dict.return_value
        
        # Create a test GoogleAccount
        GoogleAccount.objects.create(user_email=settings.GOOGLE_ACCOUNT_EMAIL, refresh_token='fake_token')
        
        url = reverse('combined_report')
        response = self.client.get(url, {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'email': settings.GOOGLE_ACCOUNT_EMAIL,
        })
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Test failed with status {response.status_code}. Response: {response.content}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the mocks were called as expected
        mock_google_ads_client.load_from_dict.assert_called_once()
        mock_fetch_costs.assert_called_once()
        mock_fetch_binom.assert_called_once()

class PermissionTests(APITestCase):
    def test_protected_views_unauthenticated(self):
        protected_urls = [
            reverse('google_ads_test'),
            reverse('generate_report'),
            reverse('google_ads_manager_check'),
            reverse('combined_report'),
            reverse('user_status'),
            reverse('logout'),
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                if 'logout' in url:
                    response = self.client.post(url)
                else:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
