from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    USER_TYPES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    type = models.CharField(
        max_length=10,
        choices=USER_TYPES
    )

    def __str__(self):
        return self.user.username