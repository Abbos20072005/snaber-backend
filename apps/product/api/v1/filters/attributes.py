import django_filters

from apps.product.models import Attribute


class AttributeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category_id")

    class Meta:
        model = Attribute
        fields = ("search", "category")
