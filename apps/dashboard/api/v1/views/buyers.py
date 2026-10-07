from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from apps.core.permissions import IsBuyer
from apps.dashboard.api.v1.serializers.buyers import (
    BuyerKpiSerializer,
    BuyerPurchaseMomentumSerializer,
    BuyerStatusMixSerializer,
    BuyerOrderTypeSplitSerializer,
    BuyerRecentActivitySerializer,
    BuyerSummarySerializer,
)
from apps.dashboard.api.v1.services.buyers import BuyerService


class BuyerKpiAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer dashboard KPIs",
        responses={200: BuyerKpiSerializer()},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_kpis(*args, **kwargs)
        return data


class BuyerPurchaseMomentumAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer purchase momentum",
        responses={200: BuyerPurchaseMomentumSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_purchase_momentum(*args, **kwargs)
        return data


class BuyerStatusMixAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer order status mix",
        responses={200: BuyerStatusMixSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_status_mix(*args, **kwargs)
        return data


class BuyerOrderTypeSplitAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer order type split",
        responses={200: BuyerOrderTypeSplitSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_order_type_split(*args, **kwargs)
        return data


class BuyerRecentBuyingActivityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer recent buying activity",
        responses={200: BuyerRecentActivitySerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_recent_buying_activity(*args, **kwargs)
        return data


class BuyerSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBuyer]

    @swagger_auto_schema(
        tags=["Buyer Dashboard"],
        operation_summary="Buyer dashboard summary",
        responses={200: BuyerSummarySerializer()},
    )
    def get(self, request, *args, **kwargs):
        data = BuyerService(request=request).get_summary(*args, **kwargs)
        return data
