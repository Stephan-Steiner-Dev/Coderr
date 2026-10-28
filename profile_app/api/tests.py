"""Tests for profile-related API endpoints and base platform information."""

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profile_app.models import UserProfile
from reviews_app.models import Review
from offers_app.models import Offer


class ProfileDetailTests(APITestCase):
    """Test retrieving individual user profiles."""

    def setUp(self):
        """Create a test user with a business profile."""
        self.user = User.objects.create_user(
            username='test_business',
            email='test@example.com',
            password='TestPass123!'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            type='business'
        )
        self.token = Token.objects.create(user=self.user)
        self.url = f'/api/profile/{self.user.id}/'

    def test_get_profile_success(self):
        """Authenticated users can retrieve a profile."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['type'], 'business')

    def test_get_profile_unauthorized(self):
        """Unauthenticated requests return HTTP 401."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_get_profile_not_found(self):
        """Unknown user IDs return HTTP 404."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/profile/99999/')

        self.assertEqual(response.status_code, 404)


class ProfileUpdateTests(APITestCase):
    """Test updating user profiles."""

    def setUp(self):
        """Create a user and profile for update tests."""
        self.user = User.objects.create_user(
            username='test_customer',
            password='TestPass123!'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            type='customer'
        )
        self.url = f'/api/profile/{self.user.id}/'

    def test_patch_own_profile(self):
        """Owners can update their own profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            self.url,
            {'first_name': 'Max', 'location': 'Berlin'},
            format='json'
        )
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.first_name, 'Max')
        self.assertEqual(self.profile.location, 'Berlin')

    def test_patch_unauthorized(self):
        """Unauthenticated users cannot update profiles."""
        response = self.client.patch(
            self.url, {'location': 'Hamburg'}, format='json'
        )
        self.assertEqual(response.status_code, 401)

    def test_patch_forbidden(self):
        """Users cannot update another user's profile."""
        other_user = User.objects.create_user(username='other_user')
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(
            self.url, {'location': 'Hamburg'}, format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_patch_not_found(self):
        """Updating an unknown profile returns HTTP 404."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            '/api/profile/99999/',
            {'location': 'Berlin'},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


class ProfileListTests(APITestCase):
    """Test business and customer profile lists."""

    def setUp(self):
        """Create authenticated users with different profile types."""
        self.business = User.objects.create_user(
            username='business_user'
        )
        self.customer = User.objects.create_user(
            username='customer_user'
        )
        UserProfile.objects.create(
            user=self.business, type='business'
        )
        UserProfile.objects.create(
            user=self.customer, type='customer'
        )

    def test_business_list(self):
        """Return only business profiles."""
        self.client.force_authenticate(user=self.business)
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_customer_list(self):
        """Return only customer profiles."""
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/api/profiles/customer/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')

    def test_business_list_unauthorized(self):
        """Reject unauthenticated business list requests."""
        response = self.client.get('/api/profiles/business/')

        self.assertEqual(response.status_code, 401)

    def test_customer_list_unauthorized(self):
        """Reject unauthenticated customer list requests."""
        response = self.client.get('/api/profiles/customer/')

        self.assertEqual(response.status_code, 401)


class BaseInfoAPITests(APITestCase):
    """Test public platform statistics."""

    def setUp(self):
        """Set up customer and business profiles for base-info tests."""
        self.url = reverse('base-info')
        self.User = get_user_model()

        self.customer = self.User.objects.create_user(
            username='base_customer',
            password='testpassword123'
        )
        self.business = self.User.objects.create_user(
            username='base_business',
            password='testpassword123'
        )

        UserProfile.objects.create(
            user=self.customer,
            type='customer'
        )
        UserProfile.objects.create(
            user=self.business,
            type='business'
        )

    def test_base_info_without_authentication(self):
        """The base-info endpoint is accessible without authentication."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_without_reviews(self):
        """A platform with no reviews should return zero metrics."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['review_count'], 0)
        self.assertEqual(response.data['average_rating'], 0)

    def test_base_info_review_count(self):
        """The total review count should reflect created reviews."""
        Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=5,
            description='Great service!'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.data['review_count'], 1)

    def test_base_info_average_rating(self):
        """Average rating should be computed across all submitted reviews."""
        second_customer = self.User.objects.create_user(
            username='second_customer',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=second_customer,
            type='customer'
        )

        Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description='Good service!'
        )
        Review.objects.create(
            business_user=self.business,
            reviewer=second_customer,
            rating=5,
            description='Excellent service!'
        )

        response = self.client.get(self.url)

        self.assertEqual(response.data['average_rating'], 4.5)

    def test_base_info_business_profile_count(self):
        """The response should include the total number of business profiles."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.data['business_profile_count'],
            1
        )

    def test_base_info_offer_count_without_offers(self):
        """The offer count should be zero when no offers exist."""
        response = self.client.get(self.url)

        self.assertEqual(response.data['offer_count'], 0)