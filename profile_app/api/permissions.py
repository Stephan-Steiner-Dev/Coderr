"""Access-control rules for profile endpoints."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow reading profiles but restrict editing to the owner."""

    def has_object_permission(self, request, view, obj):
        """Allow safe requests and restrict changes to the profile owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj.user_id == request.user.id