from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Chat center (conversation) is disabled for the frontend
# from apps.chat.api.v1.serializers.conversations import ConversationListSerializer
from apps.core.permissions import IsAdmin, IsBuyer
from apps.order.api.v1.serializers.order import (
    OrderCreateSerializer,
    OrderListSerializer,
)
from apps.order.api.v1.services.order import OrderService


class OrderListView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer | IsAdmin]

    @swagger_auto_schema(
        responses={200: OrderListSerializer(many=True)},
        tags=["Order"],
        operation_description="API to get all orders with filters",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by order ID, buyer or product name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "created_from",
                openapi.IN_QUERY,
                description="Filter by creation date start (ISO 8601 datetime)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                "created_to",
                openapi.IN_QUERY,
                description="Filter by creation date end (ISO 8601 datetime)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
        ],
    )
    def get(self, request):
        return OrderService(request=request).get_all_orders()

    @swagger_auto_schema(
        responses={201: OrderListSerializer},
        request_body=OrderCreateSerializer,
        tags=["Order"],
        operation_description="API to create a new order (from the cart when no items are sent)",
    )
    def post(self, request):
        return OrderService(request=request).create_order()


# Chat center (order conversation) is disabled for the frontend
# class OrderConversationView(APIView):
#     permission_classes = [IsAuthenticated, IsBuyer | IsAdmin]
#
#     @swagger_auto_schema(
#         responses={200: ConversationListSerializer},
#         tags=["Order"],
#         operation_description="API to get the conversation related to a specific order",
#     )
#     def get(self, request, pk):
#         return OrderService(request=request).get_order_conversation(pk)


class OrderDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), (IsBuyer | IsAdmin)()]

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        tags=["Order"],
        operation_description="API to get details of a specific order",
    )
    def get(self, request, pk):
        return OrderService(request=request).get_order(pk)

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Order"],
        operation_description="API to delete a specific order",
    )
    def delete(self, request, pk):
        return OrderService(request=request).delete_order(pk)
