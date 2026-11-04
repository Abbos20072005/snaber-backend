from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.product.api.v1.serializers.families import (
    FamilyDetailSerializer,
    FamilyListSerializer,
    FamilyWriteSerializer,
    VariantBulkCreateSerializer,
)
from apps.product.api.v1.services.families import FamilyService


class FamilyListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: FamilyListSerializer(many=True)},
        tags=["Product family"],
        operation_description="API to get all product families",
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Search by family name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                description="Filter families by category ID (includes sub-categories)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return FamilyService(request=request).get_families(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: FamilyDetailSerializer},
        request_body=FamilyWriteSerializer,
        tags=["Product family"],
        operation_description="API to create a product family"
        " and attach products to it",
    )
    def post(self, request, *args, **kwargs):
        return FamilyService(request=request).create_family(*args, **kwargs)


class FamilyDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: FamilyDetailSerializer},
        tags=["Product family"],
        operation_description="API to get certain product family with its variants",
    )
    def get(self, request, *args, **kwargs):
        return FamilyService(request=request).get_family(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: FamilyDetailSerializer},
        request_body=FamilyWriteSerializer,
        tags=["Product family"],
        operation_description="API to update certain product family",
    )
    def patch(self, request, *args, **kwargs):
        return FamilyService(request=request).update_family(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Product family"],
        operation_description="API to delete a family, its variants stay as products",
    )
    def delete(self, request, *args, **kwargs):
        return FamilyService(request=request).delete_family(*args, **kwargs)


class FamilyVariantsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={201: FamilyDetailSerializer},
        request_body=VariantBulkCreateSerializer,
        tags=["Product family"],
        operation_description="API to create variants of a family"
        " by copying a base product",
    )
    def post(self, request, *args, **kwargs):
        return FamilyService(request=request).create_variants(*args, **kwargs)
