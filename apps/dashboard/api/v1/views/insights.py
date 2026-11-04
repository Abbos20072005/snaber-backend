from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.dashboard.api.v1.serializers.insights import (
    AbandonedCartsSerializer,
    OverviewSerializer,
    StockAlertsSerializer,
)
from apps.dashboard.api.v1.services.insights import InsightsService


class OverviewAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "period",
                openapi.IN_QUERY,
                description="7d, 30d, 90d or 365d (default 30d)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: OverviewSerializer()},
        tags=["Dashboard"],
        operation_description="KPIs of the selected period next to the previous "
        "period of the same length, plus a daily revenue and orders series",
    )
    def get(self, request, *args, **kwargs):
        return InsightsService(request=request).get_overview(
            request.query_params.get("period")
        )


class AbandonedCartsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: AbandonedCartsSerializer()},
        tags=["Dashboard"],
        operation_description="Carts with items that were not touched for a day",
    )
    def get(self, request, *args, **kwargs):
        return InsightsService(request=request).get_abandoned_carts()


class StockAlertsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: StockAlertsSerializer()},
        tags=["Dashboard"],
        operation_description="Low stock, out of stock and not selling products",
    )
    def get(self, request, *args, **kwargs):
        return InsightsService(request=request).get_stock_alerts()
