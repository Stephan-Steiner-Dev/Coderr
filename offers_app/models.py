"""Database models for offers and offer packages."""
from django.conf import settings
from django.db import models


class Offer(models.Model):
    """Represent an offer created by a user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="offers"
    )
    title = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="offer_images/",
        blank=True,
        null=True
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Document the   str   behavior."""
        return self.title


class OfferDetail(models.Model):
    """Represent a package belonging to an offer."""

    OFFER_TYPES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name="details"
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10,
        choices=OFFER_TYPES
    )

    class Meta:
        """Define model metadata and configuration."""
        constraints = [
            models.UniqueConstraint(
                fields=["offer", "offer_type"],
                name="unique_offer_type_per_offer"
            )
        ]

    def __str__(self):
        """Document the   str   behavior."""
        return self.title
    