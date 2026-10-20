from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.api.v1.serializers import OrderCreateSerializer, OrderRetrieveSerializer
from apps.orders.api.v1.throttling import OrderRateThrottle
from apps.orders.models import Order


class OrderCreateAPIView(generics.CreateAPIView):
    """Savatdan buyurtma. To'lov yo'q: menejer qo'ng'iroq qilib tasdiqlaydi."""

    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()
    throttle_classes = (OrderRateThrottle,)
    throttle_scope = "orders"

    def get_throttles(self):
        # Buyurtma yaratilgach shu nusxalar orqali sanaladi.
        if not hasattr(self, "_throttles"):
            self._throttles = super().get_throttles()
        return self._throttles

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Throttle bilan bir xil manzil: NUM_PROXIES hisobga olinadi.
        context["ip_address"] = OrderRateThrottle().get_ident(self.request)
        return context

    @extend_schema(
        request=OrderCreateSerializer,
        responses={201: OrderRetrieveSerializer},
        description=(
            "Narx bazadan olinadi; javobdagi `items` va `total` buyurtma haqiqatda "
            "qabul qilingan narxlar. Bir manzildan ORDERS_THROTTLE_RATE tadan ko'p "
            "buyurtma qabul qilinmaydi (429), xato to'ldirilgan forma sanalmaydi."
        ),
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        for throttle in self.get_throttles():
            throttle.record()

        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(OrderRetrieveSerializer(order).data, status=status.HTTP_201_CREATED)
