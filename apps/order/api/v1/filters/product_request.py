import django_filters
from django.db.models import Q

from apps.order.models import ProductRequest


class ProductRequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")

    class Meta:
        model = ProductRequest
        fields = ("status", "search")

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(buyer__full_name__icontains=value)
            | Q(buyer__phone_number__icontains=value)
            | Q(items__name__icontains=value)
        ).distinct()
