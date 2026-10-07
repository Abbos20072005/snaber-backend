import django_filters
from django.db.models import Count, Q

from apps.company.models import Company, Industry, Region


class CompanyFilter(django_filters.FilterSet):
    SORT_CHOICES = (
        ("new", "New"),
        ("old", "Old"),
        ("most_products", "Most products"),
        ("most_ordered", "Most ordered"),
    )

    search = django_filters.CharFilter(method="search_filter")
    sort = django_filters.ChoiceFilter(choices=SORT_CHOICES, method="sort_filter")
    is_popular = django_filters.BooleanFilter(method="is_popular_filter")
    region = django_filters.CharFilter(field_name="region")
    industry = django_filters.CharFilter(method="industry_filter")
    product_type = django_filters.CharFilter(field_name="owner_products__product_type")

    class Meta:
        model = Company
        fields = ("search", "sort", "is_popular")

    def industry_filter(self, queryset, name, value):
        industry_ids = value.split(",")
        return queryset.filter(
            industries__id__in=industry_ids
        ).distinct()

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(name_uz__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_en__icontains=value)
        )

    def sort_filter(self, queryset, name, value):
        if value == "old":
            return queryset.order_by("created_at")
        if value == "most_products":
            return queryset.annotate(
                products_count=Count("owner_products", distinct=True)
            ).order_by("-products_count", "-created_at")
        if value == "most_ordered":
            return queryset.annotate(
                orders_count=Count("company_orders", distinct=True)
            ).order_by("-orders_count", "-created_at")
        return queryset.order_by("-created_at")

    def is_popular_filter(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.annotate(
            orders_count=Count("company_orders", distinct=True)
        ).order_by("-orders_count", "-created_at")


class CompanyDraftFilter(django_filters.FilterSet):
    SORT_CHOICES = (
        ("new", "New"),
        ("old", "Old"),
    )

    search = django_filters.CharFilter(method="search_filter")
    sort = django_filters.ChoiceFilter(choices=SORT_CHOICES, method="sort_filter")
    status = django_filters.CharFilter()

    class Meta:
        model = Company
        fields = ("search", "sort")

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(name_uz__icontains=value)
            | Q(name_ru__icontains=value)
            | Q(name_en__icontains=value)
        )

    def sort_filter(self, queryset, name, value):
        if value.lower == "old":
            return queryset.order_by("created_at")
        return queryset.order_by("-created_at")


class IndustryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")

    class Meta:
        model = Industry
        fields = ("search",)

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )


class RegionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="search_filter")

    class Meta:
        model = Region
        fields = ("search",)

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
        )