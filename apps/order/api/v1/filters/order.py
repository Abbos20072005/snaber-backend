import django_filters
from django.db.models import Q

from apps.order.models import Order


class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")
    order_type = django_filters.CharFilter(lookup_expr="iexact")
    company = django_filters.NumberFilter(field_name="company_id")
    is_closed = django_filters.BooleanFilter()

    budget_min = django_filters.NumberFilter(
        field_name="budget", lookup_expr="gte"
    )
    budget_max = django_filters.NumberFilter(
        field_name="budget", lookup_expr="lte"
    )

    deadline_from = django_filters.DateTimeFilter(
        field_name="deadline", lookup_expr="gte"
    )
    deadline_to = django_filters.DateTimeFilter(
        field_name="deadline", lookup_expr="lte"
    )

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
            "status",
            "order_type",
            "company",
            "budget_min",
            "budget_max",
            "deadline_from",
            "deadline_to",
            "created_from",
            "created_to",
            "search",
            "is_closed"
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
            | Q(company__name__icontains=value)
            | Q(items__product_variant__product__name__icontains=value)
        ).distinct()
