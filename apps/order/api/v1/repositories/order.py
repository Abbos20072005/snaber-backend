from django.db import transaction

from apps.authentication.models import User
from apps.order.api.v1.filters.order import OrderFilter
from apps.order.models import Order, OrderItem

ORDER_PREFETCH = (
    "items__product__unit",
    "items__product__images",
)


class OrderRepository:
    def get_all(self, user, query_params):
        qs = (
            Order.objects.select_related("buyer")
            .prefetch_related(*ORDER_PREFETCH)
            .order_by("-created_at")
        )

        if user.role != User.Roles.ADMIN:
            qs = qs.filter(buyer=user)

        return OrderFilter(query_params, queryset=qs).qs

    def get_by_id(self, pk):
        return (
            Order.objects.select_related("buyer")
            .prefetch_related(*ORDER_PREFETCH)
            .filter(id=pk)
            .first()
        )

    def create(self, buyer, validated_data):
        items_data = validated_data.pop("items", [])
        with transaction.atomic():
            order = Order.objects.create(buyer=buyer, **validated_data)
            self._handle_items(order, items_data)
            order.save()
        return order

    def _handle_items(self, order, items_data):
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

    def create_order_from_cart(self, buyer, cart_items):
        with transaction.atomic():
            order = Order.objects.create(buyer=buyer)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                )
            order.save()
            return order

    def delete(self, pk):
        order = self.get_by_id(pk)
        if order:
            order.delete()
            return True
        return False
