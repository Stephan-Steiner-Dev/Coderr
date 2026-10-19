
from django.db.models import Q
from rest_framework.exceptions import ValidationError


class OfferFilters:
    """Validate and apply offer list query parameters."""

    def __init__(self, params):
        self.params = params

    def apply(self, queryset):
        self.validate()
        queryset = self.filter_creator(queryset)
        queryset = self.filter_price(queryset)
        queryset = self.filter_delivery(queryset)
        return self.filter_search(queryset)

    def validate(self):
        allowed = {
            "creator_id", "min_price", "max_delivery_time",
            "search", "ordering", "page", "page_size"
        }
        for key in self.params:
            if key not in allowed:
                raise ValidationError({key: "Unknown parameter."})
        self.validate_ordering()

    def validate_ordering(self):
        value = self.params.get("ordering")
        allowed = {
            "updated_at", "-updated_at",
            "min_price", "-min_price"
        }
        if value and value not in allowed:
            raise ValidationError({"ordering": "Invalid ordering."})

    def number(self, name, number_type, minimum=0):
        value = self.params.get(name)
        if value is None:
            return None

        try:
            number = number_type(value)
            if not number.is_finite() if hasattr(number, "is_finite") else False:
                raise ValueError()
            if number < minimum:
                raise ValueError()
        except (ValueError, TypeError, ArithmeticError):
            raise ValidationError({name: "Invalid number."})

        return number

    def filter_creator(self, queryset):
        creator = self.number("creator_id", int)
        if creator is not None:
            queryset = queryset.filter(user_id=creator)
        return queryset

    def filter_price(self, queryset):
        from decimal import Decimal

        price = self.number("min_price", Decimal)
        if price is not None:
            queryset = queryset.filter(min_price__gte=price)
        return queryset

    def filter_delivery(self, queryset):
        days = self.number("max_delivery_time", int)
        if days is not None:
            queryset = queryset.filter(min_delivery_time__lte=days)
        return queryset

    def filter_search(self, queryset):
        search = self.params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )
        return queryset
