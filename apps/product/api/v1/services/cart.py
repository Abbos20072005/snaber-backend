import uuid
from rest_framework import status

from apps.core.exceptions import (
    ObjectIsNotAvailableException,
    ObjectNotFoundException,
)
from apps.core.services import BaseService
from apps.core.utils import set_guest_session_cookie
from apps.order.api.v1.repositories.order import OrderRepository
from apps.order.api.v1.serializers.order import OrderListSerializer
from apps.product.api.v1.repositories.cart import CartRepository
from apps.product.api.v1.serializers.cart import (
    CartCreateSerializer,
    CartItemSerializer,
    CartListSerializer,
    CartResponseSerializer,
    CartUpdateSerializer,
)
from apps.product.api.v1.utils.cart import get_cart_item_total_price
from apps.product.models import CartItem


class CartService(BaseService):
    def __init__(self, request, product_id=None):
        super().__init__(request)
        self.db = CartRepository()
        self.order_db = OrderRepository()
        self.product_id = product_id

    def post(self, *args, **kwargs):
        serializer = CartCreateSerializer(
            data=self.request.data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data.get("product")
        quantity = serializer.validated_data.get("quantity")

        if self.request.user.is_authenticated:
            cart = self.db.get_cart(user=self.request.user.id)
            if not cart:
                cart = self.db.create_cart(user=self.request.user)
        else:
            session_key = self.request.COOKIES.get("sessionid")
            if not session_key:
                session_key = str(uuid.uuid4())

            cart = self.db.get_cart(session_key=session_key)
            if not cart:
                cart = self.db.create_cart(session_key=session_key)

        existing_item = CartItem.objects.filter(cart=cart, product=product).first()

        if existing_item:
            if quantity <= 0:
                existing_item.delete()
                cart_item = None
            else:
                if quantity > product.stock_quantity:
                    raise ObjectIsNotAvailableException("Object is not available")
                existing_item.quantity = quantity
                existing_item.save(update_fields=["quantity"])
                cart_item = existing_item
        else:
            if quantity <= 0:
                raise ObjectNotFoundException("Object not found in cart")
            if quantity > product.stock_quantity:
                raise ObjectIsNotAvailableException("Object is not available")
            cart_item = self.db.create_cart_item(
                cart=cart, product=product, quantity=quantity
            )

        response = self.get_response_object(
            cart_item or cart,
            CartItemSerializer if cart_item else CartListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

        if not self.request.user.is_authenticated:
            set_guest_session_cookie(response, session_key)

        return response

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            items = self.db.get_cart_items(user=self.request.user)
        else:
            items = self.db.get_cart_items(
                session_key=self.request.COOKIES.get("sessionid")
            )

        return self.get_response_object(
            {
                "items": items,
                "total_amount": sum(get_cart_item_total_price(item) for item in items),
                "products": len(items),
            },
            CartResponseSerializer,
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

    def delete(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            cart_item = self.db.get_cart_by_product(
                product_id=self.product_id,
                user=self.request.user,
            )
        else:
            cart_item = self.db.get_cart_by_product(
                product_id=self.product_id,
                session_key=self.request.COOKIES.get("sessionid"),
            )

        if not cart_item:
            raise ObjectNotFoundException("Object not found")

        cart_item.delete()

        return self.get_response_object(
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

    def patch(self, *args, **kwargs):
        quantity = self.request.data.get("quantity")

        if self.request.user.is_authenticated:
            cart_item = self.db.get_cart_by_product(
                product_id=self.product_id,
                user=self.request.user,
            )
        else:
            cart_item = self.db.get_cart_by_product(
                product_id=self.product_id,
                session_key=self.request.COOKIES.get("sessionid"),
            )

        if not cart_item:
            raise ObjectNotFoundException("Object not found")

        if int(quantity) > cart_item.product.stock_quantity:
            raise ObjectIsNotAvailableException("Object is not available")

        cart_item = self.db.update_cart_quantity(cart_item, quantity)

        return self.get_response_object(
            cart_item,
            CartUpdateSerializer,
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

    def checkout(self, *args, **kwargs):
        items = self.db.get_cart_items(user=self.request.user)

        if not items:
            raise ObjectNotFoundException("Cart is empty")

        order = self.order_db.create_order_from_cart(
            buyer=self.request.user, cart_items=items
        )
        self.db.clear_cart(user=self.request.user)

        return self.get_response(
            self.order_db.get_by_id(order.id),
            OrderListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )
