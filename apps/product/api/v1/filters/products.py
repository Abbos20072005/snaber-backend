import django_filters
from django.db.models import Count, Q

from apps.product.models import AttributeValue, Category, Product


class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")
    category = django_filters.NumberFilter(method="filter_category")
    product_type = django_filters.ChoiceFilter(choices=Product.ProductType.choices)
    price_type = django_filters.ChoiceFilter(choices=Product.PriceType.choices)
    price_min = django_filters.NumberFilter(
        field_name="price_min",
        lookup_expr="gte",
    )
    price_max = django_filters.NumberFilter(
        field_name="price_min",
        lookup_expr="lte",
    )
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Product
        fields = (
            "category",
            "product_type",
            "price_type",
            "price_min",
            "price_max",
            "is_active",
        )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(sku__icontains=value)
            | Q(product_variants__sku_variant__icontains=value)
        ).distinct()

    def filter_category(self, queryset, name, value):
        descendant_ids = self._get_descendant_category_ids(value)
        return queryset.filter(category_id__in=descendant_ids)

    def _get_descendant_category_ids(self, category_id):
        ids = [category_id]
        children = Category.objects.filter(parent_id=category_id).values_list(
            "id", flat=True
        )
        for child_id in children:
            ids.extend(self._get_descendant_category_ids(child_id))
        return ids


class ProductDynamicFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")
    category = django_filters.NumberFilter(method="filter_category")
    price_min = django_filters.NumberFilter(field_name="price_min", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price_min", lookup_expr="lte")
    product_type = django_filters.CharFilter(field_name="product_type")
    is_popular = django_filters.BooleanFilter(method="filter_popular")
    values = django_filters.BaseInFilter(
        field_name="product_variants__product_attribute_values__attribute_value_id",
        method="filter_by_attribute_values",
    )
    company = django_filters.CharFilter(field_name="owner")

    class Meta:
        model = Product
        fields = (
            "search",
            "category",
            "price_min",
            "price_max",
            "product_type",
            "is_popular",
            "values",
            "company",
        )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(sku__icontains=value)
            | Q(product_variants__sku_variant__icontains=value)
        ).distinct()

    def filter_category(self, queryset, name, value):
        descendant_ids = self._get_descendant_category_ids(value)
        return queryset.filter(category_id__in=descendant_ids)

    def _get_descendant_category_ids(self, category_id):
        ids = [category_id]
        children = Category.objects.filter(parent_id=category_id).values_list(
            "id", flat=True
        )
        for child_id in children:
            ids.extend(self._get_descendant_category_ids(child_id))
        return ids

    def filter_popular(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.annotate(
            orders_count=Count("product_variants__order_items__order", distinct=True)
        ).order_by("-orders_count", "-created_at").distinct()

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
            product_variants__product_attribute_values__attribute_id__in=attribute_ids,
            product_variants__product_attribute_values__attribute_value_id__in=value_ids,
        ).distinct()
