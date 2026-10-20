from rest_framework import status

from apps.authentication.models import User
from apps.core.exceptions import ObjectNotFoundException, ValidationError
from apps.core.services import BaseService
from apps.order.api.v1.repositories.order import OrderRepository
from apps.order.api.v1.serializers.order import (
    OrderCreateSerializer,
    OrderListSerializer,
)
from apps.product.models import CartItem


class OrderService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = OrderRepository()

    def get_all_orders(self):
        orders = self.db.get_all(
            self.request.user, query_params=self.request.query_params
        )
        return self.get_paginated_response(
            orders, OrderListSerializer, context={"request": self.request}
        )

    def get_order(self, pk):
        order = self.db.get_by_id(pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self._verify_order_access(order, self.request.user)
        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def create_order(self):
        serializer = OrderCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        items_data = serializer.validated_data.get("items", [])
        if not items_data:
            cart_items = CartItem.objects.filter(
                cart__user=self.request.user
            ).select_related("product")
            if not cart_items:
                raise ObjectNotFoundException(message="Cart is empty")
            items_data = [
                {"product": cart_item.product, "quantity": cart_item.quantity}
                for cart_item in cart_items
            ]
            cart_items.delete()

        for item in items_data:
            product = item["product"]
            if item["quantity"] > product.stock_quantity:
                raise ValidationError(
                    message=f"Available quantity is {product.stock_quantity}",
                    message_key="quantity_exceeds_available",
                )

        order = self.db.create(self.request.user, {"items": items_data})

        return self.get_response(
            order,
            OrderListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def delete_order(self, pk):
        order = self.db.get_by_id(pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self.db.delete(pk)
        return self.get_response_object(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _verify_order_access(order, user):
        if user.role == User.Roles.ADMIN:
            return
        if order.buyer != user:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
