import uuid
from rest_framework import status

from apps.core.exceptions import (
    ObjectIsNotAvailableException,
    ObjectNotFoundException,
)
from apps.core.services import BaseService
from apps.order.api.v1.repositories.order import OrderRepository
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

    def _get_available_quantity(self, product_variant, attribute_stock=None):
        if attribute_stock:
            return attribute_stock.quantity
        return product_variant.stock_quantity

    def post(self, *args, **kwargs):
        serializer = CartCreateSerializer(
            data=self.request.data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)

        product_variant = serializer.validated_data.get("product")
        quantity = serializer.validated_data.get("quantity")
        attribute_stock = serializer.validated_data.get("attribute_stock")
        deadline = serializer.validated_data.get("deadline")

        raw_attributes = serializer.validated_data.get("attributes", [])
        attributes = [
            {
                "attribute": a["attribute"].id,
                "value_option": a["value_option"].id if a.get("value_option") else None,
                "value": a.get("value", ""),
            }
            for a in raw_attributes
        ]

        if attribute_stock and attribute_stock.variant != product_variant:
            raise ObjectIsNotAvailableException(
                "Attribute stock does not belong to this variant"
            )

        available = self._get_available_quantity(product_variant, attribute_stock)

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

        cart_filter = {"cart": cart, "product": product_variant}
        if attribute_stock:
            cart_filter["attribute_stock"] = attribute_stock

        # Find existing item with matching attributes to avoid overwriting
        # different variant selections (e.g. size L vs size M) on the same product
        existing_item = None
        normalized_new = sorted(
            attributes,
            key=lambda a: (
                a.get("attribute", 0),
                a.get("value_option") or 0,
                a.get("value", ""),
            ),
        )
        for item in CartItem.objects.filter(**cart_filter):
            normalized_existing = sorted(
                item.attributes or [],
                key=lambda a: (
                    a.get("attribute", 0),
                    a.get("value_option") or 0,
                    a.get("value", ""),
                ),
            )
            if normalized_new == normalized_existing:
                existing_item = item
                break

        if existing_item:
            if quantity <= 0:
                existing_item.delete()
                cart_item = None
            else:
                if not product_variant or quantity > available:
                    raise ObjectIsNotAvailableException("Object is not available")
                existing_item.quantity = quantity
                existing_item.attributes = attributes
                existing_item.deadline = deadline
                existing_item.save(update_fields=["quantity", "attributes", "deadline"])
                cart_item = existing_item
        else:
            if quantity <= 0:
                raise ObjectNotFoundException("Object not found in cart")
            if not product_variant or quantity > available:
                raise ObjectIsNotAvailableException("Object is not available")
            cart_item = self.db.create_cart_item(
                cart=cart,
                product=product_variant,
                quantity=quantity,
                company=product_variant.product.owner,
                attribute_stock=attribute_stock,
                attributes=attributes,
                deadline=deadline,
            )

        response = self.get_response_object(
            cart_item or cart,
            CartItemSerializer if cart_item else CartListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

        if not self.request.user.is_authenticated:
            response.set_cookie(
                "sessionid",
                session_key,
                max_age=60 * 60 * 24 * 10,
                httponly=True,
                samesite="Lax",
            )

        return response

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            grouped = self.db.get_cart_items_grouped_by_company(user=self.request.user)
        else:
            session_key = self.request.COOKIES.get("sessionid")
            grouped = self.db.get_cart_items_grouped_by_company(session_key=session_key)

        groups_list = [
            {"company": company, "items": items} for company, items in grouped.items()
        ]
        all_items = [item for items in grouped.values() for item in items]
        total_amount = sum(get_cart_item_total_price(item) or 0 for item in all_items)
        products = len({item.product_id for item in all_items if item.product_id})
        companies = len(grouped)

        return self.get_response_object(
            {
                "groups": groups_list,
                "total_amount": total_amount,
                "products": products,
                "companies": companies,
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
        product_variant = self.db.get_product_variant_by_product_id(
            self.product_id,
        )

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

        if not product_variant:
            raise ObjectIsNotAvailableException("Object is not available")

        available = self._get_available_quantity(
            product_variant, cart_item.attribute_stock
        )

        if int(quantity) > available:
            raise ObjectIsNotAvailableException("Object is not available")

        cart_item = self.db.update_cart_quantity(cart_item, quantity)

        return self.get_response_object(
            cart_item,
            CartUpdateSerializer,
            context={"request": self.request},
            status_code=status.HTTP_200_OK,
        )

    def checkout(self, *args, **kwargs):
        grouped = self.db.get_cart_items_grouped_by_company(user=self.request.user)

        if not grouped:
            raise ObjectNotFoundException("Cart is empty")

        order_ids = []
        for company, items in grouped.items():
            items_data = []
            for item in items:
                if item.product:
                    item_data = {
                        "product_variant": item.product,
                        "quantity": item.quantity,
                    }
                    if item.attribute_stock:
                        item_data["attribute_stock"] = item.attribute_stock
                    if item.attributes:
                        item_data["attributes"] = item.attributes
                    items_data.append(item_data)

            if items_data:
                order_type = self._detect_order_type(items_data)
                order = self.order_db.create_order_from_cart_group(
                    buyer=self.request.user,
                    company=company,
                    items_data=items_data,
                    order_type=order_type,
                )
                self._create_order_conversation(order)
                order_ids.append(order.id)

        self.db.clear_cart(user=self.request.user)

        from apps.order.api.v1.repositories.order import OrderRepository

        orders = OrderRepository().get_all_by_ids(order_ids)

        from apps.order.api.v1.serializers.order import OrderListSerializer

        return self.get_response(
            orders,
            OrderListSerializer,
            context={"request": self.request},
            many=True,
            status_code=status.HTTP_201_CREATED,
        )
