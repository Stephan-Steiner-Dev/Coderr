"""Tests for offer API endpoints."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from profile_app.models import UserProfile


class OfferListTests(APITestCase):
    """Test the offer list endpoint."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.user = get_user_model().objects.create_user(
            username="testbusiness",
            first_name="John",
            last_name="Doe"
        )
        self.url = reverse("offer-list")

    def create_offer(self):
        """Create offer."""
        return Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website design"
        )

    def create_offer_detail(self, offer, offer_type, price, days):
        """Create offer detail."""
        return OfferDetail.objects.create(
            offer=offer,
            title=offer_type.title(),
            revisions=2,
            delivery_time_in_days=days,
            price=price,
            features=["Responsive Design"],
            offer_type=offer_type
        )

    def create_offer_details(self, offer):
        """Create offer details."""
        packages = [
            ("basic", 100, 7),
            ("standard", 250, 5),
            ("premium", 500, 3)
        ]
        for offer_type, price, days in packages:
            self.create_offer_detail(offer, offer_type, price, days)

    def get_first_offer(self):
        """Return first offer."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["results"][0]

    def test_get_empty_offer_list(self):
        """Test that get empty offer list."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_get_offer_list_with_one_offer(self):
        """Test that get offer list with one offer."""
        self.create_offer()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Website Design"
        )

    def test_offer_contains_user_details(self):
        """Test that offer contains user details."""
        self.create_offer()

        user_details = self.get_first_offer()["user_details"]

        self.assertEqual(user_details["first_name"], "John")
        self.assertEqual(user_details["last_name"], "Doe")
        self.assertEqual(user_details["username"], "testbusiness")

    def test_offer_contains_details(self):
        """Test that offer contains details."""
        offer = self.create_offer()
        self.create_offer_details(offer)

        details = self.get_first_offer()["details"]

        self.assertEqual(len(details), 3)

    def test_offer_contains_min_price(self):
        """Test that offer contains min price."""
        offer = self.create_offer()
        self.create_offer_details(offer)

        min_price = self.get_first_offer()["min_price"]

        self.assertEqual(min_price, 100)

    def test_offer_contains_min_delivery_time(self):
        """Test that offer contains min delivery time."""
        offer = self.create_offer()
        self.create_offer_details(offer)

        min_delivery_time = self.get_first_offer()["min_delivery_time"]

        self.assertEqual(min_delivery_time, 3)


class OfferCreateTests(APITestCase):
    """Test the offer creation endpoint."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.user = get_user_model().objects.create_user(
            username="testbusiness",
            password="TestPassword123!"
        )
        UserProfile.objects.create(
            user=self.user,
            type="business"
        )
        self.url = reverse("offer-list")
        self.client.force_authenticate(user=self.user)
        self.data = self.get_valid_data()

    def get_valid_data(self):
        """Return valid data."""
        return {
            "title": "Website Design",
            "description": "Professional website design",
            "details": [
                self.make_detail("basic", 100),
                self.make_detail("standard", 250),
                self.make_detail("premium", 500),
            ]
        }

    def make_detail(self, offer_type, price):
        """Build detail."""
        return {
            "title": offer_type.title(),
            "revisions": 2,
            "delivery_time_in_days": 5,
            "price": price,
            "features": ["Responsive Design"],
            "offer_type": offer_type
        }

    def test_business_user_can_create_offer(self):
        """Test that business user can create offer."""
        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)

    def test_response_contains_detail_ids(self):
        """Test that response contains detail ids."""
        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(len(response.data["details"]), 3)
        for detail in response.data["details"]:
            self.assertIn("id", detail)

    def test_rejects_incomplete_details(self):
        """Test that rejects incomplete details."""
        self.data["details"].pop()

        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_rejects_duplicate_offer_types(self):
        """Test that rejects duplicate offer types."""
        self.data["details"][1]["offer_type"] = "basic"

        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 0)

    def test_customer_cannot_create_offer(self):
        """Test that customer cannot create offer."""
        self.user.profile.type = "customer"
        self.user.profile.save()

        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_offer(self):
        """Test that unauthenticated user cannot create offer."""
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.url, self.data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), 0)


class OfferDetailTests(APITestCase):
    """Test retrieving, updating and deleting a single offer."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.user = get_user_model().objects.create_user(
            username="owner",
            password="TestPassword123!"
        )
        self.other_user = get_user_model().objects.create_user(
            username="other",
            password="TestPassword123!"
        )
        self.offer = Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website design"
        )
        self.create_details()
        self.url = reverse(
            "offer-detail", kwargs={"pk": self.offer.pk}
        )
        self.client.force_authenticate(user=self.user)

    def create_details(self):
        """Create details."""
        for offer_type, price in [
            ("basic", 100),
            ("standard", 250),
            ("premium", 500)
        ]:
            OfferDetail.objects.create(
                offer=self.offer,
                title=offer_type.title(),
                revisions=2,
                delivery_time_in_days=5,
                price=price,
                features=["Responsive Design"],
                offer_type=offer_type
            )

    def test_authenticated_user_can_get_offer(self):
        """Test that authenticated user can get offer."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.offer.id)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(response.data["min_price"], 100)

    def test_unauthenticated_user_cannot_get_offer(self):
        """Test that unauthenticated user cannot get offer."""
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_get_nonexistent_offer(self):
        """Test that get nonexistent offer."""
        url = reverse("offer-detail", kwargs={"pk": 99999})

        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

    def test_owner_can_update_offer(self):
        """Test that owner can update offer."""
        response = self.client.patch(
            self.url,
            {"title": "Updated Website Design"},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.title, "Updated Website Design")

    def test_owner_can_update_single_detail(self):
        """Test that owner can update single detail."""
        detail = self.offer.details.get(offer_type="basic")
        original_id = detail.id

        response = self.client.patch(
            self.url,
            {"details": [
                {"offer_type": "basic", "price": 150}
            ]},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        detail.refresh_from_db()
        self.assertEqual(detail.id, original_id)
        self.assertEqual(detail.price, 150)
        self.assertEqual(self.offer.details.count(), 3)

    def test_other_user_cannot_update_offer(self):
        """Test that other user cannot update offer."""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {"title": "Unauthorized Update"},
            format="json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_owner_can_delete_offer(self):
        """Test that owner can delete offer."""
        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertFalse(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )
        self.assertEqual(OfferDetail.objects.count(), 0)

    def test_other_user_cannot_delete_offer(self):
        """Test that other user cannot delete offer."""
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertTrue(
            Offer.objects.filter(pk=self.offer.pk).exists()
        )


class OfferDetailItemTests(APITestCase):
    """Test retrieving a single offer detail."""

    def setUp(self):
        """Prepare shared data for this test case."""
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="TestPassword123!"
        )
        offer = Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website design"
        )
        self.detail = OfferDetail.objects.create(
            offer=offer,
            title="Basic Website",
            revisions=2,
            delivery_time_in_days=7,
            price=100,
            features=["Responsive Design"],
            offer_type="basic"
        )
        self.url = reverse(
            "offer-detail-item",
            kwargs={"pk": self.detail.pk}
        )

    def test_authenticated_user_can_get_detail(self):
        """Test that authenticated user can get detail."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.detail.id)
        self.assertEqual(response.data["title"], "Basic Website")
        self.assertEqual(response.data["offer_type"], "basic")

    def test_unauthenticated_user_cannot_get_detail(self):
        """Test that unauthenticated user cannot get detail."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_nonexistent_detail_returns_404(self):
        """Test that nonexistent detail returns 404."""
        self.client.force_authenticate(user=self.user)
        url = reverse("offer-detail-item", kwargs={"pk": 99999})

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )