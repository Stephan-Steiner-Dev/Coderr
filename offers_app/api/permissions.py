"""Access-control rules for offer endpoints."""
from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """Allow only authenticated business users."""

    message = "Only business users can create offers."

    def has_permission(self, request, view):
        """Check that the request comes from an authenticated business user."""
        user = request.user
        return (
            user.is_authenticated
            and hasattr(user, "profile")
            and user.profile.type == "business"
        )


class IsOfferOwner(BasePermission):
    """Allow only the offer owner to modify or delete it."""

    message = "Only the offer owner can modify this offer."

    def has_object_permission(self, request, view, obj):
        """Check that the requesting user owns the offer."""
        return obj.user_id == request.user.id