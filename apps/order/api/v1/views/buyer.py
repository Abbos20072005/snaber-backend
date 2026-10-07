from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsBuyer
from apps.order.api.v1.serializers.order import OrderListSerializer
from apps.order.api.v1.services.buyer import BuyerOrderService


class BuyerOrderView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: OrderListSerializer(many=True)},
        tags=["Buyer Orders"],
        operation_description="API to get orders for a specific buyer",
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
    def get(self, request, pk):
        return BuyerOrderService(request=request).get(pk=pk)
