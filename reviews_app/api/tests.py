
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profile_app.models import UserProfile
from reviews_app.models import Review


User = get_user_model()


class ReviewAPITests(APITestCase):
    """Test review endpoints and permissions."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer',
            password='testpassword123'
        )
        self.other_customer = User.objects.create_user(
            username='other_customer',
            password='testpassword123'
        )
        self.business = User.objects.create_user(
            username='business',
            password='testpassword123'
        )

        UserProfile.objects.create(
            user=self.customer,
            type='customer'
        )
        UserProfile.objects.create(
            user=self.other_customer,
            type='customer'
        )
        UserProfile.objects.create(
            user=self.business,
            type='business'
        )

        self.list_url = reverse('review-list-create')

        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=5,
            description='Excellent service!'
        )

        self.detail_url = reverse(
            'review-detail',
            kwargs={'pk': self.review.pk}
        )

    def test_list_reviews_authenticated(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reviews_unauthenticated(self):
        response = self.client.get(self.list_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_filter_reviews_by_business_user(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url,
            {'business_user_id': self.business.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_reviews_by_reviewer(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url,
            {'reviewer_id': self.customer.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_invalid_filter_returns_400(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            self.list_url,
            {'business_user_id': 'abc'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_create_review(self):
        self.client.force_authenticate(user=self.other_customer)

        data = {
            'business_user': self.business.id,
            'rating': 4,
            'description': 'Very good!'
        }

        response = self.client.post(self.list_url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(Review.objects.count(), 2)
        self.assertEqual(
            response.data['reviewer'],
            self.other_customer.id
        )

    def test_create_review_unauthenticated(self):
        response = self.client.post(
            self.list_url,
            {
                'business_user': self.business.id,
                'rating': 5,
                'description': 'Great!'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_business_cannot_create_review(self):
        self.client.force_authenticate(user=self.business)

        response = self.client.post(
            self.list_url,
            {
                'business_user': self.business.id,
                'rating': 5,
                'description': 'Great!'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_duplicate_review_forbidden(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            self.list_url,
            {
                'business_user': self.business.id,
                'rating': 4,
                'description': 'Another review'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(Review.objects.count(), 1)

    def test_invalid_rating(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.post(
            self.list_url,
            {
                'business_user': self.business.id,
                'rating': 6,
                'description': 'Invalid rating'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_review_requires_business_user(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.post(
            self.list_url,
            {
                'business_user': self.customer.id,
                'rating': 5,
                'description': 'Invalid business user'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_update_own_review(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            self.detail_url,
            {
                'rating': 4,
                'description': 'Updated review'
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(
            self.review.description,
            'Updated review'
        )

    def test_cannot_update_other_review(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.patch(
            self.detail_url,
            {'rating': 1}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_cannot_change_business_user(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            self.detail_url,
            {'business_user': self.other_customer.id}
        )

        self.review.refresh_from_db()
        self.assertEqual(
            self.review.business_user,
            self.business
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_delete_own_review(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_delete_other_review(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.delete(self.detail_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(Review.objects.count(), 1)

    def test_update_nonexistent_review(self):
        self.client.force_authenticate(user=self.customer)

        url = reverse(
            'review-detail',
            kwargs={'pk': 99999}
        )

        response = self.client.patch(url, {'rating': 3})

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_delete_nonexistent_review(self):
        self.client.force_authenticate(user=self.customer)

        url = reverse(
            'review-detail',
            kwargs={'pk': 99999}
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
