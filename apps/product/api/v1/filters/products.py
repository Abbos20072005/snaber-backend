import django_filters
from django.db.models import Count, Q

from apps.product.models import AttributeValue, Category, Product


def get_descendant_category_ids(category_id):
    ids = [category_id]
    children = Category.objects.filter(parent_id=category_id).values_list(
        "id", flat=True
    )
    for child_id in children:
        ids.extend(get_descendant_category_ids(child_id))
    return ids


class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")
    category = django_filters.NumberFilter(method="filter_category")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = (
            "search",
            "category",
            "price_min",
            "price_max",
            "is_active",
            "in_stock",
        )

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(sku__icontains=value))

    def filter_category(self, queryset, name, value):
        return queryset.filter(category_id__in=get_descendant_category_ids(value))

    def filter_in_stock(self, queryset, name, value):
        if value is None:
            return queryset
        return queryset.filter(stock_quantity__gt=0) if value else queryset.filter(
            stock_quantity=0
        )


class ProductDynamicFilter(ProductFilter):
    is_popular = django_filters.BooleanFilter(method="filter_popular")
    values = django_filters.BaseInFilter(
        field_name="product_attribute_values__attribute_value_id",
        method="filter_by_attribute_values",
    )

    class Meta:
        model = Product
        fields = (
            "search",
            "category",
            "price_min",
            "price_max",
            "is_popular",
            "values",
        )

    def filter_popular(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.annotate(
            orders_count=Count("order_items__order", distinct=True)
        ).order_by("-orders_count", "-created_at")

    def filter_by_attribute_values(self, queryset, name, value):
        if not value:
            return queryset

        attribute_values = AttributeValue.objects.filter(
            id__in=value,
            attribute__is_filterable=True,
        ).values("id", "attribute_id")

        if not attribute_values:
            return queryset

        value_ids = [av["id"] for av in attribute_values]
        attribute_ids = [av["attribute_id"] for av in attribute_values]

        return queryset.filter(
            product_attribute_values__attribute_id__in=attribute_ids,
            product_attribute_values__attribute_value_id__in=value_ids,
        ).distinct()
