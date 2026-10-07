from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller
from apps.product.api.v1.serializers.values import (
    AttributeValueCreateSerializer,
    AttributeValueListSerializer,
)
from apps.product.api.v1.services.values import AttributeValueService


class AttributeValueListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]

    @swagger_auto_schema(
        responses={200: AttributeValueListSerializer(many=True)},
        tags=["Attribute value"],
        operation_description="List of attribute values by attribute ID",
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search attribute values by value",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="attribute",
                in_=openapi.IN_QUERY,
                description="Filter values by attribute (ID)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return AttributeValueService(request=request).get_values(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: AttributeValueListSerializer},
        request_body=AttributeValueCreateSerializer,
        tags=["Attribute value"],
        operation_description="Attribute value create",
    )
    def post(self, request, *args, **kwargs):
        return AttributeValueService(request=request).create_value(*args, **kwargs)


class AttributeValueUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: AttributeValueListSerializer},
        request_body=AttributeValueCreateSerializer,
        tags=["Attribute value"],
        operation_description="Attribute value update",
    )
    def patch(self, request, *args, **kwargs):
        return AttributeValueService(request=request).update_value(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Attribute value"],
        operation_description="Attribute value delete",
    )
    def delete(self, request, *args, **kwargs):
        return AttributeValueService(request=request).delete_value(*args, **kwargs)
