from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsSeller
from apps.dashboard.api.v1.serializers.sellers import (
    # BuyerEngagementSerializer,
    HeroSummarySerializer,
    KpiSerializer,
    RecentOrderSerializer,
    RevenueMomentumSerializer,
    RfqPipelineSerializer,
    SalesByCategorySerializer,
    TopProductSerializer,
)
from apps.dashboard.api.v1.services.sellers import SellerService


class SellerHeroAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: HeroSummarySerializer()},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard hero summary",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_hero_summary(*args, **kwargs)


class SellerKPIsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: KpiSerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard KPI cards",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_kpis(*args, **kwargs)


class SellerRevenueMomentumAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: RevenueMomentumSerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard revenue momentum chart",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_revenue_momentum(*args, **kwargs)


class SellerSalesByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: SalesByCategorySerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard sales by category",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_sales_by_category(*args, **kwargs)


# Chat center (buyer engagement chart) is disabled for the frontend
# class SellerBuyerEngagementAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsSeller]
#
#     @swagger_auto_schema(
#         responses={200: BuyerEngagementSerializer(many=True)},
#         tags=["Dashboard Seller"],
#         operation_description="Returns seller dashboard buyer engagement chart",
#     )
#     def get(self, request, *args, **kwargs):
#         return SellerService(request=request).get_buyer_engagement(*args, **kwargs)


class SellerRFQPipelineAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: RfqPipelineSerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard RFQ pipeline chart",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_rfq_pipeline(*args, **kwargs)


class SellerTopProductsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: TopProductSerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard top products",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_top_products(*args, **kwargs)


class SellerRecentOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        responses={200: RecentOrderSerializer(many=True)},
        tags=["Dashboard Seller"],
        operation_description="Returns seller dashboard recent orders",
    )
    def get(self, request, *args, **kwargs):
        return SellerService(request=request).get_recent_orders(*args, **kwargs)

