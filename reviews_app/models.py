"""Database model for user reviews."""
from django.conf import settings
from django.db import models


class Review(models.Model):
    """Represent a review written for a business user."""
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='written_reviews'
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Define model metadata and configuration."""
        constraints = [
            models.UniqueConstraint(
                fields=['business_user', 'reviewer'],
                name='unique_review_per_business'
            )
        ]

    def __str__(self):
        """Return a readable reviewer-to-business representation of the review."""
        return f'{self.reviewer.username} -> {self.business_user.username}'