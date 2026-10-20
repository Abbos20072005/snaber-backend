import django_filters
from django.db.models import Q

from apps.order.models import Order


class OrderFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_to = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    search = django_filters.CharFilter(method="search_filter")

    class Meta:
        model = Order
        fields = (
            "created_from",
            "created_to",
            "search",
        )

    def search_filter(self, queryset, name, value):
        try:
            int(value)
            id_filter = Q(id=int(value))
        except ValueError:
            id_filter = Q()
        return queryset.filter(
            id_filter
            | Q(buyer__full_name__icontains=value)
            | Q(buyer__email__icontains=value)
            | Q(buyer__phone_number__icontains=value)
            | Q(items__product__name__icontains=value)
        ).distinct()
