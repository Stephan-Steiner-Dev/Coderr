
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


class OfferListTests(APITestCase):
    """Test the offer list endpoint."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testbusiness",
            first_name="John",
            last_name="Doe"
        )
        self.url = reverse("offer-list")

    def create_offer(self):
        return Offer.objects.create(
            user=self.user,
            title="Website Design",
            description="Professional website design"
        )

    def create_offer_detail(self, offer, offer_type, price, days):
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
        packages = [
            ("basic", 100, 7),
            ("standard", 250, 5),
            ("premium", 500, 3)
        ]
        for offer_type, price, days in packages:
            self.create_offer_detail(offer, offer_type, price, days)

    def get_first_offer(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["results"][0]

    def test_get_empty_offer_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_get_offer_list_with_one_offer(self):
        self.create_offer()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Website Design"
        )

    def test_offer_contains_user_details(self):
        self.create_offer()

        user_details = self.get_first_offer()["user_details"]

        self.assertEqual(user_details["first_name"], "John")
        self.assertEqual(user_details["last_name"], "Doe")
        self.assertEqual(user_details["username"], "testbusiness")

    def test_offer_contains_details(self):
        offer = self.create_offer()
        self.create_offer_details(offer)

        details = self.get_first_offer()["details"]

        self.assertEqual(len(details), 3)

    def test_offer_contains_min_price(self):
        offer = self.create_offer()
        self.create_offer_details(offer)

        min_price = self.get_first_offer()["min_price"]

        self.assertEqual(min_price, 100)

    def test_offer_contains_min_delivery_time(self):
        offer = self.create_offer()
        self.create_offer_details(offer)

        min_delivery_time = self.get_first_offer()["min_delivery_time"]

        self.assertEqual(min_delivery_time, 3)
