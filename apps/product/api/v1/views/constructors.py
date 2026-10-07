from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import (
    IsAdminOrSuperAdmin,
    IsModerator,
    IsModeratorOrAdmin,
    IsSeller,
)
from apps.product.api.v1.serializers.constructors import (
    ConstructorReviewSerializer,
    ProductConstructorCreateUpdateSerializer,
    ProductConstructorDetailSerializer,
    ProductConstructorListSerializer,
    VariantConstructorCreateUpdateSerializer,
    VariantConstructorListSerializer,
)
from apps.product.api.v1.services.constructors import ConstructorService


class ConstructorListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsModerator | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: ProductConstructorListSerializer},
        tags=["Product"],
        operation_description="API to list product constructors",
    )
    def get(self, request, *args, **kwargs):
        return ConstructorService(request=request).list_constructors(*args, **kwargs)

    @swagger_auto_schema(
        request_body=ProductConstructorCreateUpdateSerializer,
        responses={201: ProductConstructorListSerializer},
        tags=["Product"],
        operation_description="API to create a product constructor",
    )
    def post(self, request, *args, **kwargs):
        return ConstructorService(request=request).create_constructor(*args, **kwargs)


class VariantConstructorCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsModerator | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        request_body=VariantConstructorCreateUpdateSerializer,
        responses={201: VariantConstructorListSerializer},
        tags=["Product"],
        operation_description="API to create a variant constructor",
    )
    def post(self, request, *args, **kwargs):
        return ConstructorService(request=request).create_variant_constructor(
            *args, **kwargs
        )


class ConstructorDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsModerator | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: ProductConstructorDetailSerializer},
        tags=["Product"],
        operation_description="API to retrieve a product constructor "
        "with its variant constructors",
    )
    def get(self, request, *args, **kwargs):
        return ConstructorService(request=request).retrieve_constructor(*args, **kwargs)

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Product"],
        operation_description="Delete a product constructor. "
        "Only admin, super admin, or the owner company can delete.",
    )
    def delete(self, request, *args, **kwargs):
        return ConstructorService(request=request).delete_constructor(*args, **kwargs)


class VariantConstructorDetailView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsModerator | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={204: "No Content"},
        tags=["Product"],
        operation_description="Delete a variant constructor. "
        "Only admin, super admin, or the owner company can delete.",
    )
    def delete(self, request, *args, **kwargs):
        return ConstructorService(request=request).delete_variant_constructor(
            *args, **kwargs
        )


class DraftProductView(APIView):
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsSeller]

    @swagger_auto_schema(
        responses={200: ProductConstructorListSerializer},
        tags=["Product"],
        operation_description="API to list pending product constructors for review",
    )
    def get(self, request, *args, **kwargs):
        return ConstructorService(request=request).list_draft_constructors(
            *args, **kwargs
        )


class DraftProductDetailView(APIView):
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsSeller]

    @swagger_auto_schema(
        request_body=ConstructorReviewSerializer,
        responses={200: ProductConstructorListSerializer},
        tags=["Product"],
        operation_description=(
            "API to review a product constructor. Set status and moderator_comment. "
            "When status is set to 'accepted', the constructor is applied to the "
            "real Product and Variant models automatically."
        ),
    )
    def patch(self, request, *args, **kwargs):
        return ConstructorService(request=request).review_constructor(*args, **kwargs)
