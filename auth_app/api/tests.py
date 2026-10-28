"""Tests for authentication API endpoints."""

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTests(APITestCase):
    """Test the user login endpoint."""

    def setUp(self):
        """Create a test user before each test."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePassword123!'
        )

    def test_login_with_valid_credentials(self):
        """Verify that valid credentials return user data and a token."""
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'SecurePassword123!'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertIn('token', response.data)


class RegistrationTests(APITestCase):
    """Test the user registration endpoint."""

    def test_registration_with_valid_data(self):
        """Verify that valid registration data returns HTTP 201 and user details."""
        response = self.client.post('/api/registration/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'repeated_password': 'SecurePassword123!',
            'type': 'customer'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)