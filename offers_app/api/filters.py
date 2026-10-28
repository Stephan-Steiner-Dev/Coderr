"""Query-parameter validation and filtering for offers."""

from django.db.models import Q
from rest_framework.exceptions import ValidationError


class OfferFilters:
    """Validate and apply offer list query parameters."""

    def __init__(self, params):
        """Store the query parameters used to filter offers."""
        self.params = params

    def apply(self, queryset):
        """Validate query parameters and apply their filters to the queryset."""
        self.validate()
        queryset = self.filter_creator(queryset)
        queryset = self.filter_price(queryset)
        queryset = self.filter_delivery(queryset)
        return self.filter_search(queryset)

    def validate(self):
        """Reject unsupported query parameters and validate ordering."""
        allowed = {
            "creator_id", "min_price", "max_delivery_time",
            "search", "ordering", "page", "page_size"
        }
        for key in self.params:
            if key not in allowed:
                raise ValidationError({key: "Unknown parameter."})
        self.validate_ordering()

    def validate_ordering(self):
        """Ensure the requested ordering field is supported."""
        value = self.params.get("ordering")
        allowed = {
            "updated_at", "-updated_at",
            "min_price", "-min_price"
        }
        if value and value not in allowed:
            raise ValidationError({"ordering": "Invalid ordering."})

    def number(self, name, number_type, minimum=0):
        """Parse and validate a non-negative numeric query parameter."""
        value = self.params.get(name)
        if value is None:
            return None
        try:
            number = number_type(value)
            if hasattr(number, "is_finite") and not number.is_finite():
                raise ValueError()
            if number < minimum:
                raise ValueError()
        except (ValueError, TypeError, ArithmeticError):
            raise ValidationError({name: "Invalid number."})
        return number

    def filter_creator(self, queryset):
        """Restrict offers to the requested creator when specified."""
        creator = self.number("creator_id", int)
        if creator is not None:
            queryset = queryset.filter(user_id=creator)
        return queryset

    def filter_price(self, queryset):
        """Restrict offers to those meeting the minimum price."""
        from decimal import Decimal

        price = self.number("min_price", Decimal)
        if price is not None:
            queryset = queryset.filter(min_price__gte=price)
        return queryset

    def filter_delivery(self, queryset):
        """Restrict offers to those within the maximum delivery time."""
        days = self.number("max_delivery_time", int)
        if days is not None:
            queryset = queryset.filter(min_delivery_time__lte=days)
        return queryset

    def filter_search(self, queryset):
        """Match offers whose title or description contains the search term."""
        search = self.params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )
        return queryset
