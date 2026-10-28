"""Access-control rules for order endpoints."""
from rest_framework.permissions import BasePermission


class IsCustomerOrReadOnly(BasePermission):
    """Allow authenticated users to read and customers to create."""

    def has_permission(self, request, view):
        """Allow reads and restrict order creation to customer profiles."""
        if request.method == "GET":
            return True

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == "customer"
        )


class IsOrderBusinessOrStaff(BasePermission):
    """Allow assigned business users to update and staff to delete."""

    def has_permission(self, request, view):
        """Allow order updates to business users and deletion to staff."""
        if request.method == "DELETE":
            return request.user.is_staff

        return (
            hasattr(request.user, "profile")
            and request.user.profile.type == "business"
        )

    def has_object_permission(self, request, view, obj):
        """Check that the user may modify or delete this order."""
        if request.method == "DELETE":
            return request.user.is_staff

        return obj.business_user == request.user