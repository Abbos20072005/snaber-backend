import django_filters

from apps.product.models import AttributeValue


class AttributeValueFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="value", lookup_expr="icontains")
    attribute = django_filters.NumberFilter(field_name="attribute_id")

    class Meta:
        model = AttributeValue
        fields = ("search", "attribute")
