from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.order.api.v1.serializers.order import OrderListSerializer
from apps.product.api.v1.serializers.cart import (
    CartCreateSerializer,
    CartListSerializer,
    CartResponseSerializer,
    CartUpdateSerializer,
)
from apps.product.api.v1.services.cart import (
    CartService,
)


class CartAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CartCreateSerializer,
        responses={200: CartListSerializer},
        tags=["Cart"],
    )
    def post(self, request, *args, **kwargs):
        return CartService(request=request).post()

    @swagger_auto_schema(
        responses={200: CartResponseSerializer},
        tags=["Cart"],
    )
    def get(self, request, *args, **kwargs):
        return CartService(request=request).get()


class CartUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=CartUpdateSerializer,
        responses={200: CartListSerializer},
        tags=["Cart"],
    )
    def patch(self, request, *args, **kwargs):
        return CartService(request=request, product_id=kwargs.get("pk")).patch()

    @swagger_auto_schema(
        responses={200: CartListSerializer},
        tags=["Cart"],
    )
    def delete(self, request, *args, **kwargs):
        return CartService(request=request, product_id=kwargs.get("pk")).delete()


class CartCheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={201: OrderListSerializer(many=True)},
        tags=["Cart"],
        operation_description=(
            "Checkout: create orders grouped by company from cart items"
        ),
    )
    def post(self, request, *args, **kwargs):
        return CartService(request=request).checkout()
