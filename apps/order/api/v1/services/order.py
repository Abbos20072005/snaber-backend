from rest_framework import status

from apps.authentication.models import User
# Chat center (conversation) is disabled for the frontend
# from apps.chat.api.v1.serializers.conversations import ConversationListSerializer
# from apps.chat.models import Conversation, Message
from apps.company.models import CompanyMember
from apps.core.exceptions import (
    ObjectNotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from apps.core.services import BaseService
from apps.notification.api.v1.repositories.notifications import NotificationRepository
from apps.notification.models import Notification
from apps.order.api.v1.repositories.order import OrderRepository
from apps.order.api.v1.serializers.order import (
    OrderCreateUpdateSerializer,
    OrderItemCreateSerializer,
    OrderItemUpdateQuantitySerializer,
    OrderListSerializer,
)
from apps.order.models import Order
from apps.product.models import CartItem, Product, Variant


class OrderService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = OrderRepository()

    def _detect_order_type(self, items_data):
        variant_ids = [
            getattr(item.get("product_variant"), "pk", item.get("product_variant"))
            for item in items_data
            if item.get("product_variant")
        ]
        if not variant_ids:
            return Order.OrderType.READY
        product_types = set(
            Variant.objects.filter(id__in=variant_ids)
            .values_list("product__product_type", flat=True)
            .distinct()
        )
        if not product_types:
            return Order.OrderType.READY
        if product_types == {Product.ProductType.READY}:
            return Order.OrderType.READY
        if product_types == {Product.ProductType.MADE_TO_ORDER}:
            return Order.OrderType.RFQ
        if product_types == {Product.ProductType.BOTH}:
            return Order.OrderType.READY
        return Order.OrderType.BOTH

    def get_all_orders(self):
        user = self.request.user
        orders = self.db.get_all(user, query_params=self.request.query_params)
        return self.get_paginated_response(
            orders, OrderListSerializer, context={"request": self.request}
        )

    def get_order(self, pk):
        order = self.db.get_by_id(pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        user = self.request.user
        if user.role not in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            is_buyer = order.buyer == user
            is_seller = CompanyMember.objects.filter(
                company=order.company, user=user
            ).exists()
            if not is_buyer and not is_seller:
                raise ObjectNotFoundException(
                    message="Order not found", message_key="order_not_found"
                )
        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def create_order(self):
        serializer = OrderCreateUpdateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        items_data = validated_data.pop("items", [])
        if not items_data:
            cart_items = CartItem.objects.filter(
                cart__user=self.request.user,
                company=validated_data["company"],
            ).select_related("product__product")
            if not cart_items:
                raise ObjectNotFoundException(message="No cart items for this company")
            deadlines = []
            for cart_item in cart_items:
                item_data = {
                    "product_variant": cart_item.product,
                    "quantity": cart_item.quantity,
                }
                if cart_item.attribute_stock:
                    item_data["attribute_stock"] = cart_item.attribute_stock
                if cart_item.attributes:
                    item_data["attributes"] = cart_item.attributes
                if cart_item.deadline:
                    deadlines.append(cart_item.deadline)
                items_data.append(item_data)
            if deadlines and "deadline" not in validated_data:
                validated_data["deadline"] = min(deadlines)
            CartItem.objects.filter(
                cart__user=self.request.user,
                company=validated_data["company"],
            ).delete()

        for item in items_data:
            variant = item.get("product_variant")
            quantity = item.get("quantity")
            if variant and quantity:
                moq = variant.moq_override or variant.product.moq
                if quantity < moq:
                    raise ValidationError(
                        message=f"Minimum order quantity is {moq}",
                        message_key="quantity_below_moq",
                    )

        if "order_type" not in validated_data:
            validated_data["order_type"] = self._detect_order_type(items_data)
        validated_data["items"] = items_data
        order = self.db.create(self.request.user, validated_data)
        # Chat center (conversation creation) is disabled for the frontend
        # self._create_order_conversation(order)

        return self.get_response(
            order,
            OrderListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    # Chat center (conversation creation) is disabled for the frontend
    # def _create_order_conversation(self, order):
    #     seller = (
    #         CompanyMember.objects.filter(
    #             company=order.company, user__role=User.Roles.SELLER
    #         )
    #         .select_related("user")
    #         .first()
    #     )
    #     conversation, created = Conversation.objects.get_or_create(
    #         order=order,
    #         defaults={
    #             "type": Conversation.Type.ORDER,
    #             "buyer": order.buyer,
    #             "seller": seller.user if seller else None,
    #         },
    #     )
    #     if created:
    #         msg = f"Order #{order.id} has been created."
    #         if order.order_type == Order.OrderType.RFQ:
    #             msg += " Start negotiating!"
    #         Message.objects.create(
    #             conversation=conversation,
    #             sender=order.buyer,
    #             system_message={
    #                 "type": "order_created",
    #                 "order_id": order.id,
    #                 "order_type": order.order_type,
    #                 "message": msg,
    #             },
    #         )

    def update_order(self, pk, partial=True):
        order = self.db.get_by_id(pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )

        serializer = OrderCreateUpdateSerializer(
            data=self.request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = self.request.user
        is_buyer = order.buyer == user
        is_seller = CompanyMember.objects.filter(
            company=order.company, user=user
        ).exists()
        is_admin = user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN)

        current_status = order.status
        new_status = validated_data.get("status")
        new_is_closed = validated_data.get("is_closed")

        if order.is_closed:
            raise PermissionDeniedException(
                message="Cannot modify a closed order.",
                message_key="order_closed",
            )

        if new_is_closed:
            if not (is_seller or is_admin):
                raise PermissionDeniedException(
                    message="You do not have permission to close this order.",
                    message_key="cannot_close_order",
                )
            order.is_closed = True
            order.save()
            self._send_order_notification(
                order.buyer,
                title_uz="Buyurtma yopildi",
                title_ru="Заказ закрыт",
                title_en="Order Closed",
                message_uz=f"Sizning #{order.id}-buyurtmangiz yopildi.",
                message_ru=f"Ваш заказ №{order.id} был закрыт.",
                message_en=f"Your order #{order.id} has been closed.",
                redirect_id=order.id,
            )
            return self.get_response(
                order, OrderListSerializer, context={"request": self.request}
            )

        if current_status in (Order.OrderStatus.ACCEPTED, Order.OrderStatus.REJECTED):
            raise PermissionDeniedException(
                message="Cannot modify a finalized order.",
                message_key="order_finalized",
            )

        new_buyer_flag = new_seller_flag = new_buyer_reject = new_seller_reject = None

        if current_status == Order.OrderStatus.NEGOTIATION:
            if new_status == Order.OrderStatus.ACCEPTED:
                new_buyer_flag = True if (is_buyer or is_admin) else None
                new_seller_flag = True if (is_seller or is_admin) else None
                new_status = None
            elif new_status == Order.OrderStatus.REJECTED:
                new_buyer_reject = True if (is_buyer or is_admin) else None
                new_seller_reject = True if (is_seller or is_admin) else None
                new_status = None

            if new_buyer_flag is not None:
                order.accepted_by_buyer = new_buyer_flag
                order.rejected_by_buyer = False

            if new_seller_flag is not None:
                if new_seller_flag and not order.accepted_by_seller:
                    self._send_order_notification(
                        order.buyer,
                        title_uz="Sotuvchi buyurtmani tasdiqladi",
                        title_ru="Продавец подтвердил заказ",
                        title_en="Order Accepted by Seller",
                        message_uz=f"Sotuvchi sizning #{order.id}-buyurtmangizni tasdiqladi.",
                        message_ru=f"Продавец подтвердил ваш заказ №{order.id}.",
                        message_en=f"The seller has accepted order #{order.id}.",
                        redirect_id=order.id,
                    )
                order.accepted_by_seller = new_seller_flag
                order.rejected_by_seller = False

            if new_buyer_reject is not None:
                order.rejected_by_buyer = new_buyer_reject
                order.accepted_by_buyer = False

            if new_seller_reject is not None:
                if new_seller_reject and not order.rejected_by_seller:
                    self._send_order_notification(
                        order.buyer,
                        title_uz="Sotuvchi buyurtmani rad etdi",
                        title_ru="Продавец отклонил заказ",
                        title_en="Order Rejected by Seller",
                        message_uz=f"Sotuvchi sizning #{order.id}-buyurtmangizni rad etdi.",
                        message_ru=f"Продавец отклонил ваш заказ №{order.id}.",
                        message_en=f"The seller has rejected order #{order.id}.",
                        redirect_id=order.id,
                    )
                order.rejected_by_seller = new_seller_reject
                order.accepted_by_seller = False

            if order.accepted_by_buyer and order.accepted_by_seller:
                new_status = Order.OrderStatus.ACCEPTED
                order.rejected_by_buyer = order.rejected_by_seller = False
            elif order.rejected_by_buyer and order.rejected_by_seller:
                new_status = Order.OrderStatus.REJECTED
                order.accepted_by_buyer = order.accepted_by_seller = False

            details_changed = any(
                k in validated_data and validated_data[k] != getattr(order, k)
                for k in ("budget", "deadline")
            )
            if details_changed:
                order.accepted_by_buyer = order.accepted_by_seller = False
                order.rejected_by_buyer = order.rejected_by_seller = False
                for k in ("budget", "deadline"):
                    if k in validated_data:
                        setattr(order, k, validated_data[k])
            elif (
                not new_status
                and new_buyer_flag is None
                and new_seller_flag is None
                and new_buyer_reject is None
                and new_seller_reject is None
            ):
                for k, v in validated_data.items():
                    if k not in ("status", "items"):
                        setattr(order, k, v)

        if new_status and new_status != current_status:
            if (current_status, new_status) == (
                Order.OrderStatus.NEGOTIATION,
                Order.OrderStatus.ACCEPTED,
            ):
                order.status = Order.OrderStatus.ACCEPTED
                self._send_order_notification(
                    order.buyer,
                    title_uz="Buyurtma tasdiqlandi",
                    title_ru="Заказ подтверждён",
                    title_en="Order Accepted",
                    message_uz=f"Sizning #{order.id}-buyurtmangiz har ikki tomon tomonidan tasdiqlandi.",
                    message_ru=f"Ваш заказ №{order.id} был подтверждён обеими сторонами.",
                    message_en=f"Your order #{order.id} has been accepted by both parties.",
                    redirect_id=order.id,
                )
            elif (current_status, new_status) == (
                Order.OrderStatus.NEGOTIATION,
                Order.OrderStatus.REJECTED,
            ):
                order.status = Order.OrderStatus.REJECTED
                self._send_order_notification(
                    order.buyer,
                    title_uz="Buyurtma rad etildi",
                    title_ru="Заказ отклонён",
                    title_en="Order Rejected",
                    message_uz=f"Sizning #{order.id}-buyurtmangiz rad etildi.",
                    message_ru=f"Ваш заказ №{order.id} был отклонён.",
                    message_en=f"Your order #{order.id} has been rejected.",
                    redirect_id=order.id,
                )
            else:
                raise PermissionDeniedException(
                    f"Cannot transition order from {current_status} to {new_status}."
                )
        order.save()

        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def _send_order_notification(self, user, title_uz, title_ru, title_en, message_uz, message_ru, message_en, redirect_id=None):
        NotificationRepository().create_notification(
            user=user,
            title_uz=title_uz,
            title_ru=title_ru,
            title_en=title_en,
            message_uz=message_uz,
            message_ru=message_ru,
            message_en=message_en,
            notification_type=Notification.NotificationType.ORDER,
            redirect_id=redirect_id,
        )

    def _verify_order_access(self, order, user):
        if user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            return
        is_buyer = order.buyer == user
        is_seller = CompanyMember.objects.filter(
            company=order.company, user=user
        ).exists()
        if not is_buyer and not is_seller:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )

    def update_item_quantity(self, order_pk, item_pk):
        order = self.db.get_by_id(order_pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self._verify_order_access(order, self.request.user)
        if order.is_closed:
            raise PermissionDeniedException(
                message="Cannot modify a closed order.", message_key="order_closed"
            )
        if order.status != Order.OrderStatus.NEGOTIATION:
            raise PermissionDeniedException(
                message="Items can only be modified during negotiation.",
                message_key="order_not_in_negotiation",
            )
        item = self.db.get_order_item(order_pk, item_pk)
        if not item:
            raise ObjectNotFoundException(
                message="Order item not found", message_key="order_item_not_found"
            )
        serializer = OrderItemUpdateQuantitySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        variant = item.product_variant
        available = (
            item.attribute_stock.quantity
            if item.attribute_stock
            else variant.stock_quantity
        )
        moq = variant.moq_override or variant.product.moq
        if quantity < moq:
            raise ValidationError(
                message=f"Minimum order quantity is {moq}",
                message_key="quantity_below_moq",
            )
        if quantity > available:
            raise ValidationError(
                message=f"Available quantity is {available}",
                message_key="quantity_exceeds_available",
            )
        self.db.update_item_quantity(item, quantity)
        order.accepted_by_buyer = False
        order.accepted_by_seller = False
        order.save()
        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def add_item(self, order_pk):
        order = self.db.get_by_id(order_pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self._verify_order_access(order, self.request.user)
        if order.is_closed:
            raise PermissionDeniedException(
                message="Cannot modify a closed order.", message_key="order_closed"
            )
        if order.status != Order.OrderStatus.NEGOTIATION:
            raise PermissionDeniedException(
                message="Items can only be added during negotiation.",
                message_key="order_not_in_negotiation",
            )
        serializer = OrderItemCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        item_data = serializer.validated_data
        variant = item_data["product_variant"]
        quantity = item_data["quantity"]
        available = (
            item_data["attribute_stock"].quantity
            if item_data.get("attribute_stock")
            else variant.stock_quantity
        )
        moq = variant.moq_override or variant.product.moq
        if quantity < moq:
            raise ValidationError(
                message=f"Minimum order quantity is {moq}",
                message_key="quantity_below_moq",
            )
        if quantity > available:
            raise ValidationError(
                message=f"Available quantity is {available}",
                message_key="quantity_exceeds_available",
            )
        self.db.add_item(order, item_data)
        order.accepted_by_buyer = False
        order.accepted_by_seller = False
        order.save()
        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def remove_item(self, order_pk, item_pk):
        order = self.db.get_by_id(order_pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self._verify_order_access(order, self.request.user)
        if order.is_closed:
            raise PermissionDeniedException(
                message="Cannot modify a closed order.", message_key="order_closed"
            )
        if order.status != Order.OrderStatus.NEGOTIATION:
            raise PermissionDeniedException(
                message="Items can only be removed during negotiation.",
                message_key="order_not_in_negotiation",
            )
        item = self.db.get_order_item(order_pk, item_pk)
        if not item:
            raise ObjectNotFoundException(
                message="Order item not found", message_key="order_item_not_found"
            )
        self.db.delete_item(item)
        order.accepted_by_buyer = False
        order.accepted_by_seller = False
        order.save()
        return self.get_response(
            order, OrderListSerializer, context={"request": self.request}
        )

    def delete_order(self, pk):
        order = self.db.get_by_id(pk)
        if not order:
            raise ObjectNotFoundException(
                message="Order not found", message_key="order_not_found"
            )
        self.db.delete(pk)
        return self.get_response_object(status_code=status.HTTP_204_NO_CONTENT)

    # Chat center (order conversation) is disabled for the frontend
    # def get_order_conversation(self, pk):
    #     order = self.db.get_by_id(pk)
    #     if not order:
    #         raise ObjectNotFoundException(
    #             message="Order not found", message_key="order_not_found"
    #         )
    #     user = self.request.user
    #     if user.role not in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
    #         is_buyer = order.buyer == user
    #         is_seller = CompanyMember.objects.filter(
    #             company=order.company, user=user
    #         ).exists()
    #         if not is_buyer and not is_seller:
    #             raise ObjectNotFoundException(
    #                 message="Order not found", message_key="order_not_found"
    #             )
    #     conversation = Conversation.objects.filter(order=order).first()
    #     if not conversation:
    #         raise ObjectNotFoundException(
    #             message="Conversation not found", message_key="conversation_not_found"
    #         )
    #     return self.get_response_object(
    #         conversation,
    #         ConversationListSerializer,
    #         context={"request": self.request},
    #     )

