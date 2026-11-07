import django_filters
from django.db.models import Q

from apps.authentication.models import User


class UserFilter(django_filters.FilterSet):
    role = django_filters.ChoiceFilter(choices=User.Roles.choices)
    search = django_filters.CharFilter(method="search_filter")
    has_orders = django_filters.BooleanFilter(method="has_orders_filter")

    class Meta:
        model = User
        fields = (
            "role",
            "is_active",
            "is_blocked",
            "is_verified",
            "search",
            "has_orders",
        )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(full_name__icontains=value)
            | Q(email__icontains=value)
            | Q(phone_number__icontains=value)
        )

    def has_orders_filter(self, queryset, name, value):
        # `orders_count` is annotated by the repository.
        if value:
            return queryset.filter(orders_count__gt=0)
        return queryset.filter(orders_count=0)
