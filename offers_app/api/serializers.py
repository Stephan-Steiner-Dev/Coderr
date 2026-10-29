"""Serializers for offers and offer packages."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db.models import Min
from django.db import transaction

from offers_app.models import Offer, OfferDetail


class OfferUserSerializer(serializers.ModelSerializer):
    """Serialize basic information about an offer creator."""

    class Meta:
        """Define the user fields included in offer responses."""
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "username",
        ]
        read_only_fields = fields


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serialize links to offer details."""

    url = serializers.SerializerMethodField()

    class Meta:
        """Define the fields exposed for offer-detail links."""
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        """Return the URL for the serialized offer detail."""
        return f"/offerdetails/{obj.id}/"


class OfferListSerializer(serializers.ModelSerializer):
    """Serialize offers for the offer list endpoint."""

    details = OfferDetailLinkSerializer(
        many=True, read_only=True
    )
    user_details = OfferUserSerializer(
        source="user", read_only=True
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        """Define the fields included in offer-list responses."""
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]


class OfferDetailCreateSerializer(serializers.ModelSerializer):
    """Validate offer package data."""

    class Meta:
        """Define the fields accepted for an offer package."""
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Serialize a single offer."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )
    min_delivery_time = serializers.IntegerField(read_only=True)

    class Meta:
        """Define the read-only fields returned for one offer."""
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time"
        ]
        read_only_fields = fields


class OfferUpdateSerializer(serializers.ModelSerializer):
    """Update an offer and its existing packages."""

    details = OfferDetailCreateSerializer(
        many=True, required=False
    )

    class Meta:
        """Define the fields accepted when updating an offer."""
        model = Offer
        fields = ["id", "title", "image", "description", "details"]
        read_only_fields = ["id"]

    def validate_details(self, details):
        """Validate package types in the update data."""
        types = []
        for detail in details:
            offer_type = detail.get("offer_type")
            if offer_type is None:
                raise serializers.ValidationError(
                    "Each detail requires an offer_type."
                )
            types.append(offer_type)
        if len(types) != len(set(types)):
            raise serializers.ValidationError(
                "Each offer type may only appear once."
            )
        return details

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the offer and any supplied package data atomically."""
        details = validated_data.pop("details", [])
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        self.update_details(instance, details)
        return instance

    def update_details(self, offer, details):
        """Apply package updates to the existing offer packages."""
        for detail_data in details:
            offer_type = detail_data.pop("offer_type")
            detail = offer.details.filter(
                offer_type=offer_type
            ).first()
            if detail is None:
                raise serializers.ValidationError(
                    {"details": f"Unknown offer type: {offer_type}"}
                )
            self.update_detail(detail, detail_data)

    def update_detail(self, detail, data):
        """Apply the supplied fields to one offer package."""
        for field, value in data.items():
            setattr(detail, field, value)
        detail.save()


class OfferCreateSerializer(serializers.ModelSerializer):
    """Create an offer with three packages."""

    details = OfferDetailCreateSerializer(many=True)

    class Meta:
        """Define the fields accepted when creating an offer."""
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]

    def validate_details(self, details):
        """Require exactly one package of each supported type."""
        types = [detail["offer_type"] for detail in details]
        required = ["basic", "premium", "standard"]

        if sorted(types) != required:
            raise serializers.ValidationError(
                "Exactly one basic, standard and premium package required."
            )
        return details

    @transaction.atomic
    def create(self, validated_data):
        """Create an offer and its packages atomically."""
        details = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user,
            **validated_data
        )
        for detail in details:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer
