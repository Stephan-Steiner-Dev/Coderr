"""Tests for order API endpoints."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order
from profile_app.models import UserProfile


class OrderListCreateTests(APITestCase):
    """Test listing and creating orders."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.customer = self.create_user("customer", "customer")
        self.business = self.create_user("business", "business")
        self.other_user = self.create_user("other", "customer")
        self.offer = Offer.objects.create(
            user=self.business,
            title="Logo Design",
            description="Professional logo design"
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo", "Source File"],
            offer_type="basic"
        )
        self.url = reverse("order-list-create")

    def create_user(self, username, user_type):
        """Create a user with a profile."""
        user = User.objects.create_user(
            username=username, password="testpassword123"
        )
        UserProfile.objects.create(user=user, type=user_type)
        return user

    def authenticate(self, user):
        """Authenticate a user using their token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_get_orders_requires_authentication(self):
        """Test that get orders requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_orders_returns_only_related_orders(self):
        """Test that get orders returns only related orders."""
        self.authenticate(self.customer)
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo"],
            offer_type="basic"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_orders_excludes_unrelated_orders(self):
        """Test that get orders excludes unrelated orders."""
        self.authenticate(self.other_user)
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo"],
            offer_type="basic"
        )
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)

    def test_post_order_as_customer(self):
        """Test that post order as customer."""
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {"offer_detail_id": self.detail.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(response.data["status"], "in_progress")
        self.assertEqual(response.data["business_user"], self.business.id)

    def test_post_order_as_business_forbidden(self):
        """Test that post order as business forbidden."""
        self.authenticate(self.business)
        response = self.client.post(
            self.url, {"offer_detail_id": self.detail.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_order_requires_authentication(self):
        """Test that post order requires authentication."""
        response = self.client.post(
            self.url, {"offer_detail_id": self.detail.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_order_without_offer_detail_id(self):
        """Test that post order without offer detail id."""
        self.authenticate(self.customer)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_order_with_invalid_id(self):
        """Test that post order with invalid id."""
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {"offer_detail_id": 99999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_order_with_negative_id(self):
        """Test that post order with negative id."""
        self.authenticate(self.customer)
        response = self.client.post(
            self.url, {"offer_detail_id": -1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderDetailTests(APITestCase):
    """Test updating and deleting orders."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.customer = self.create_user("customer", "customer")
        self.business = self.create_user("business", "business")
        self.other_business = self.create_user("other", "business")
        self.staff = self.create_user("staff", "customer", True)
        self.order = Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo", "Source File"],
            offer_type="basic"
        )
        self.url = reverse("order-detail", args=[self.order.id])

    def create_user(self, username, user_type, is_staff=False):
        """Create a user with a profile."""
        user = User.objects.create_user(
            username=username,
            password="testpassword123",
            is_staff=is_staff
        )
        UserProfile.objects.create(user=user, type=user_type)
        return user

    def authenticate(self, user):
        """Authenticate a user using their token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_patch_order_as_business(self):
        """Test that patch order as business."""
        self.authenticate(self.business)
        response = self.client.patch(
            self.url, {"status": "completed"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

    def test_patch_order_as_customer_forbidden(self):
        """Test that patch order as customer forbidden."""
        self.authenticate(self.customer)
        response = self.client.patch(
            self.url, {"status": "completed"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_as_other_business_forbidden(self):
        """Test that patch order as other business forbidden."""
        self.authenticate(self.other_business)
        response = self.client.patch(
            self.url, {"status": "completed"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_order_requires_authentication(self):
        """Test that patch order requires authentication."""
        response = self.client.patch(
            self.url, {"status": "completed"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_order_invalid_status(self):
        """Test that patch order invalid status."""
        self.authenticate(self.business)
        response = self.client.patch(
            self.url, {"status": "pending"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_rejects_other_fields(self):
        """Test that patch order rejects other fields."""
        self.authenticate(self.business)
        response = self.client.patch(
            self.url, {"price": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_order_not_found(self):
        """Test that patch order not found."""
        self.authenticate(self.business)
        url = reverse("order-detail", args=[99999])
        response = self.client.patch(
            url, {"status": "completed"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_as_staff(self):
        """Test that delete order as staff."""
        self.authenticate(self.staff)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.pk).exists())

    def test_delete_order_as_customer_forbidden(self):
        """Test that delete order as customer forbidden."""
        self.authenticate(self.customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_as_business_forbidden(self):
        """Test that delete order as business forbidden."""
        self.authenticate(self.business)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_requires_authentication(self):
        """Test that delete order requires authentication."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_order_not_found(self):
        """Test that delete order not found."""
        self.authenticate(self.staff)
        url = reverse("order-detail", args=[99999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderCountTests(APITestCase):
    """Test active and completed order counts."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.business = self.create_user("business", "business")
        self.customer = self.create_user("customer", "customer")
        self.other_business = self.create_user("other", "business")
        self.authenticate(self.customer)
        self.active_url = reverse("order-count", args=[self.business.id])
        self.completed_url = reverse(
            "completed-order-count", args=[self.business.id]
        )

    def create_user(self, username, user_type):
        """Create a user with a profile."""
        user = User.objects.create_user(
            username=username, password="testpassword123"
        )
        UserProfile.objects.create(user=user, type=user_type)
        return user

    def authenticate(self, user):
        """Authenticate a user using their token."""
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_order(self, business, order_status):
        """Create an order with a specific status."""
        return Order.objects.create(
            customer_user=self.customer,
            business_user=business,
            title="Logo Design",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo"],
            offer_type="basic",
            status=order_status
        )

    def test_active_order_count(self):
        """Test that active order count."""
        self.create_order(self.business, "in_progress")
        self.create_order(self.business, "in_progress")
        self.create_order(self.business, "completed")
        response = self.client.get(self.active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 2)

    def test_completed_order_count(self):
        """Test that completed order count."""
        self.create_order(self.business, "completed")
        self.create_order(self.business, "completed")
        self.create_order(self.business, "in_progress")
        response = self.client.get(self.completed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_active_order_count_without_orders(self):
        """Test that active order count without orders."""
        response = self.client.get(self.active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 0)

    def test_completed_order_count_without_orders(self):
        """Test that completed order count without orders."""
        response = self.client.get(self.completed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 0)

    def test_active_count_excludes_other_business_orders(self):
        """Test that active count excludes other business orders."""
        self.create_order(self.other_business, "in_progress")
        response = self.client.get(self.active_url)
        self.assertEqual(response.data["order_count"], 0)

    def test_completed_count_excludes_other_business_orders(self):
        """Test that completed count excludes other business orders."""
        self.create_order(self.other_business, "completed")
        response = self.client.get(self.completed_url)
        self.assertEqual(response.data["completed_order_count"], 0)

    def test_active_count_requires_authentication(self):
        """Test that active count requires authentication."""
        self.client.credentials()
        response = self.client.get(self.active_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_completed_count_requires_authentication(self):
        """Test that completed count requires authentication."""
        self.client.credentials()
        response = self.client.get(self.completed_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_active_count_business_not_found(self):
        """Test that active count business not found."""
        url = reverse("order-count", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_count_business_not_found(self):
        """Test that completed count business not found."""
        url = reverse("completed-order-count", args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_active_count_customer_id_returns_404(self):
        """Test that active count customer id returns 404."""
        url = reverse("order-count", args=[self.customer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_completed_count_customer_id_returns_404(self):
        """Test that completed count customer id returns 404."""
        url = reverse(
            "completed-order-count", args=[self.customer.id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)