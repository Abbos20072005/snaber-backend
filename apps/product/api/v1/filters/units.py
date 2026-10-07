import django_filters

from apps.product.models import Unit


class UnitFilter(django_filters.FilterSet):
    unit = django_filters.CharFilter(field_name="unit", lookup_expr="icontains")

    class Meta:
        model = Unit
        fields = ("unit",)
