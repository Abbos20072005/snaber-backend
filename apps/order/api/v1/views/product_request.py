from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin, IsBuyer
from apps.core.services import ServiceDefaultResponseSerializer
from apps.order.api.v1.serializers.product_request import (
    ProductRequestCreateSerializer,
    ProductRequestSerializer,
    ProductRequestUpdateSerializer,
    WantedProductSerializer,
)
from apps.order.api.v1.services.product_request import ProductRequestService


class ProductRequestListView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated(), (IsBuyer | IsAdmin)()]

    @swagger_auto_schema(
        responses={200: ProductRequestSerializer(many=True)},
        tags=["Product request"],
        operation_description="Own requests of the buyer, all requests for admins",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by buyer name, phone or product name",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request):
        return ProductRequestService(request=request).get_all_requests()

    @swagger_auto_schema(
        request_body=ProductRequestCreateSerializer,
        responses={201: ServiceDefaultResponseSerializer},
        tags=["Product request"],
        operation_description="Ask for products the buyer could not find: a list "
        "of names, a photo or an Excel file. Without a login the phone number "
        "is required and the buyer is registered with it",
    )
    def post(self, request):
        return ProductRequestService(request=request).create_request()


class WantedProductListView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        responses={200: WantedProductSerializer(many=True)},
        tags=["Product request"],
        operation_description="Products the buyers could not find, most asked first",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by product name",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request):
        return ProductRequestService(request=request).get_wanted_products()


class ProductRequestDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsAdmin()]
        return [IsAuthenticated(), (IsBuyer | IsAdmin)()]

    @swagger_auto_schema(
        responses={200: ProductRequestSerializer},
        tags=["Product request"],
        operation_description="Request details",
    )
    def get(self, request, pk):
        return ProductRequestService(request=request).get_request(pk)

    @swagger_auto_schema(
        request_body=ProductRequestUpdateSerializer,
        responses={200: ProductRequestSerializer},
        tags=["Product request"],
        operation_description="Answer a request and change its status",
    )
    def patch(self, request, pk):
        return ProductRequestService(request=request).update_request(pk)
