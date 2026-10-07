import django_filters
from django.db.models import Count

from apps.product.models import Category


class CategoryFilter(django_filters.FilterSet):
    is_popular = django_filters.BooleanFilter(method="filter_popular")

    class Meta:
        model = Category
        fields = ("is_popular",)

    def filter_popular(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.annotate(
            orders_count=Count(
                "category_products__product_variants__order_items__order", distinct=True
            )
        ).order_by("-orders_count", "-created_at")
