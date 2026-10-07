from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller
from apps.product.api.v1.serializers.attributes import AttributeFilterSerializer
from apps.product.api.v1.serializers.variants import (
    VariantCreateUpdateSerializer,
    VariantDetailSerializer,
    VariantListSerializer,
)
from apps.product.api.v1.services.constructors import ConstructorService
from apps.product.api.v1.services.variants import (
    VariantService,
)
from apps.product.models import Variant


class ProductVariantCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={201: VariantListSerializer},
        request_body=VariantCreateUpdateSerializer,
        tags=["Variant"],
        operation_description="API to create product variant for product",
    )
    def post(self, request, *args, **kwargs):
        return VariantService(request=request).create_variant(*args, **kwargs)


class ProductVariantUpdateDeleteDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: VariantListSerializer},
        request_body=VariantCreateUpdateSerializer,
        tags=["Variant"],
        operation_description="API to update certain variant "
        "constructor by constructor id",
    )
    def patch(self, request, *args, **kwargs):
        return ConstructorService(request=request).update_variant_via_constructor(
            *args, **kwargs
        )

    @swagger_auto_schema(
        tags=["Variant"],
        operation_description="API to delete certain variant of product",
    )
    def delete(self, request, *args, **kwargs):
        return VariantService(request=request).delete_variant(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: VariantDetailSerializer},
        tags=["Variant"],
        operation_description="API to get detail "
        "informaation certain variant of product",
    )
    def get(self, request, *args, **kwargs):
        return VariantService(request=request).get_variant(*args, **kwargs)


class VariantRFQAttributesView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: AttributeFilterSerializer(many=True)},
        tags=["Variant"],
        operation_description="Get available RFQ attributes for a variant "
        "(attributes configured for this variant with their possible values).",
    )
    def get(self, request, id):
        variant = (
            Variant.objects.filter(id=id)
            .select_related("product__category")
            .prefetch_related(
                "product_attribute_values__attribute__attribute_values",
            )
            .first()
        )
        if not variant:
            return Response(
                {"detail": "Variant not found."}, status=status.HTTP_404_NOT_FOUND
            )

        attributes = variant.product_attribute_values.values_list(
            "attribute", flat=True
        ).distinct()

        from apps.product.models import Attribute

        attrs = Attribute.objects.filter(id__in=attributes).prefetch_related(
            "attribute_values"
        )

        serializer = AttributeFilterSerializer(attrs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
