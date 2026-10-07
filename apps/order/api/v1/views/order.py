from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Chat center (conversation) is disabled for the frontend
# from apps.chat.api.v1.serializers.conversations import ConversationListSerializer
from apps.core.permissions import IsAdminOrSuperAdmin, IsBuyer, IsSeller
from apps.order.api.v1.serializers.order import (
    OrderCreateUpdateSerializer,
    OrderItemCreateSerializer,
    OrderItemUpdateQuantitySerializer,
    OrderListSerializer,
)
from apps.order.api.v1.services.order import OrderService


class OrderListView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer | IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: OrderListSerializer(many=True)},
        tags=["Order"],
        operation_description="API to get all orders with filters",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by order ID, buyer/company/product name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status (negotiation, accepted, rejected)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "is_closed",
                openapi.IN_QUERY,
                description="Filter by closed state (true, false)",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "order_type",
                openapi.IN_QUERY,
                description="Filter by type (ready, rfq, both)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "budget_min",
                openapi.IN_QUERY,
                description="Minimum budget filter",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "budget_max",
                openapi.IN_QUERY,
                description="Maximum budget filter",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "deadline_from",
                openapi.IN_QUERY,
                description="Filter by deadline start (ISO 8601 datetime)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                "deadline_to",
                openapi.IN_QUERY,
                description="Filter by deadline end (ISO 8601 datetime)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
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
        request_body=OrderCreateUpdateSerializer,
        tags=["Order"],
        operation_description="API to create a new order (Ready or RFQ)",
    )
    def post(self, request):
        return OrderService(request=request).create_order()


# Chat center (order conversation) is disabled for the frontend
# class OrderConversationView(APIView):
#     permission_classes = [IsAuthenticated, IsBuyer | IsSeller | IsAdminOrSuperAdmin]
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
        if self.request.method in ("PATCH", "PUT"):
            return [IsAuthenticated(), (IsBuyer | IsSeller | IsAdminOrSuperAdmin)()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated(), (IsBuyer | IsSeller | IsAdminOrSuperAdmin)()]

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        tags=["Order"],
        operation_description="API to get details of a specific order",
    )
    def get(self, request, pk):
        return OrderService(request=request).get_order(pk)

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        request_body=OrderCreateUpdateSerializer,
        tags=["Order"],
        operation_description="API to partially update a specific order",
    )
    def patch(self, request, pk):
        return OrderService(request=request).update_order(pk, partial=True)

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        request_body=OrderCreateUpdateSerializer,
        tags=["Order"],
        operation_description="API to fully update a specific order",
    )
    def put(self, request, pk):
        return OrderService(request=request).update_order(pk, partial=False)

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Order"],
        operation_description="API to delete a specific order",
    )
    def delete(self, request, pk):
        return OrderService(request=request).delete_order(pk)


class OrderItemView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer | IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        request_body=OrderItemUpdateQuantitySerializer,
        tags=["Order"],
        operation_description="Update quantity of an order item (negotiation only)",
    )
    def patch(self, request, pk, item_pk):
        return OrderService(request=request).update_item_quantity(pk, item_pk)

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        request_body=OrderItemCreateSerializer,
        tags=["Order"],
        operation_description="Add a new item to an order (negotiation only)",
    )
    def post(self, request, pk):
        return OrderService(request=request).add_item(pk)

    @swagger_auto_schema(
        responses={200: OrderListSerializer},
        tags=["Order"],
        operation_description="Remove an item from an order (negotiation only)",
    )
    def delete(self, request, pk, item_pk):
        return OrderService(request=request).remove_item(pk, item_pk)

