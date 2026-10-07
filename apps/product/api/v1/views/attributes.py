from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller
from apps.product.api.v1.serializers.attributes import (
    AttributeCreateSerializer,
    AttributeListSerializer,
)
from apps.product.api.v1.services.attributes import (
    AttributeService,
)


class AttributeListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated(), (IsAdminOrSuperAdmin | IsSeller)()]

    @swagger_auto_schema(
        responses={200: AttributeListSerializer},
        tags=["Attribute"],
        operation_description="Attributes list",
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search attributes by name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                description="Filter attributes by category ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return AttributeService(request=request).get_attributes(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: AttributeListSerializer},
        request_body=AttributeCreateSerializer,
        tags=["Attribute"],
        operation_description="Attribute create",
    )
    def post(self, request, *args, **kwargs):
        return AttributeService(request=request).create_attribute(*args, **kwargs)


class AttributeUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: AttributeListSerializer},
        request_body=AttributeCreateSerializer,
        tags=["Attribute"],
        operation_description="Attribute update",
    )
    def patch(self, request, *args, **kwargs):
        return AttributeService(request=request).update_attribute(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Attribute"],
        operation_description="Attribute delete",
    )
    def delete(self, request, *args, **kwargs):
        return AttributeService(request=request).delete_attribute(*args, **kwargs)


class CategoryFilterableAttributesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Attribute"],
        operation_description="Get price range and filterable attributes. "
        "Optionally filter by category ID.",
        manual_parameters=[
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                description="Category ID to filter attributes "
                "and price range (optional)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return AttributeService(request=request).get_filterable_attributes(
            *args, **kwargs
        )
