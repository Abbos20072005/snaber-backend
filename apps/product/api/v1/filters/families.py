import django_filters

from apps.product.api.v1.filters.products import get_descendant_category_ids
from apps.product.models import ProductFamily


class FamilyFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = django_filters.NumberFilter(method="filter_category")

    class Meta:
        model = ProductFamily
        fields = ("search", "category")

    def filter_category(self, queryset, name, value):
        return queryset.filter(category_id__in=get_descendant_category_ids(value))
