from django.db import transaction
from django.db.models import Count, Max, Min, Sum
from django.db.models.functions import Lower

from apps.authentication.models import User
from apps.order.api.v1.filters.product_request import ProductRequestFilter
from apps.order.models import ProductRequest, ProductRequestItem


class ProductRequestRepository:
    def get_all(self, user, query_params):
        qs = (
            ProductRequest.objects.select_related("buyer")
            .prefetch_related("items")
            .order_by("-created_at")
        )

        if user.role != User.Roles.ADMIN:
            qs = qs.filter(buyer=user)

        return ProductRequestFilter(query_params, queryset=qs).qs

    def get_wanted(self, search):
        # Products asked for and not answered yet, the same name is one row.
        qs = ProductRequestItem.objects.exclude(
            request__status=ProductRequest.Status.DONE
        )
        if search:
            qs = qs.filter(name__icontains=search)
        return (
            qs.annotate(key=Lower("name"))
            .values("key")
            .annotate(
                product_name=Min("name"),
                requests_count=Count("request", distinct=True),
                total_quantity=Sum("quantity"),
                last_requested_at=Max("created_at"),
            )
            .order_by("-requests_count", "-last_requested_at")
        )

    def get_by_id(self, pk):
        return (
            ProductRequest.objects.select_related("buyer")
            .prefetch_related("items")
            .filter(id=pk)
            .first()
        )

    def create(self, buyer, validated_data):
        items = validated_data.pop("items", [])
        with transaction.atomic():
            product_request = ProductRequest.objects.create(
                buyer=buyer, **validated_data
            )
            ProductRequestItem.objects.bulk_create(
                ProductRequestItem(request=product_request, **item) for item in items
            )
        return self.get_by_id(product_request.id)
