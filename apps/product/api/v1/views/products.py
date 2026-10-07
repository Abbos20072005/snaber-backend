from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller
from apps.product.api.v1.serializers.products import (
    GlobalSearchSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from apps.product.api.v1.services.products import ProductService


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: ProductListSerializer},
        tags=["Product"],
        operation_description="API to get all products with pagination",
        manual_parameters=[
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                description="Filter products by category ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="product_type",
                in_=openapi.IN_QUERY,
                description="Filter products by product_type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="price_type",
                in_=openapi.IN_QUERY,
                description="Filter products by price_type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="price_min",
                in_=openapi.IN_QUERY,
                description="Filter products by price_min",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                name="price_max",
                in_=openapi.IN_QUERY,
                description="Filter products by price_max",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                name="is_active",
                in_=openapi.IN_QUERY,
                description="Filter products by is_active",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                name="status",
                in_=openapi.IN_QUERY,
                description="Filter products by status",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).get_products(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: ProductListSerializer},
        request_body=ProductCreateUpdateSerializer,
        tags=["Product"],
        operation_description="API to create product",
    )
    def post(self, request, *args, **kwargs):
        return ProductService(request=request).create_product(*args, **kwargs)


class ProductDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={201: ProductDetailSerializer},
        tags=["Product"],
        operation_description="API to get certain product",
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).get_product(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Product"],
        operation_description="API to delete certain product",
    )
    def delete(self, request, *args, **kwargs):
        return ProductService(request=request).delete_product(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: ProductListSerializer},
        request_body=ProductCreateUpdateSerializer,
        tags=["Product"],
        operation_description="API to update certain product "
        "constructor by constructor id",
    )
    def patch(self, request, *args, **kwargs):
        return ProductService(request=request).update_product(*args, **kwargs)


class ProductTopView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={201: ProductListSerializer},
        tags=["Product"],
        operation_description="API to get top products",
        manual_parameters=[
            openapi.Parameter(
                name="category",
                in_=openapi.IN_QUERY,
                description="Filter products by category ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="product_type",
                in_=openapi.IN_QUERY,
                description="Filter products by product_type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="price_type",
                in_=openapi.IN_QUERY,
                description="Filter products by price_type",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="price_min",
                in_=openapi.IN_QUERY,
                description="Filter products by price_min",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                name="price_max",
                in_=openapi.IN_QUERY,
                description="Filter products by price_max",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                name="is_popular",
                in_=openapi.IN_QUERY,
                description="Filter products by is_popular",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                name="values",
                in_=openapi.IN_QUERY,
                description="Filter products by attribute value IDs",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
            ),
            openapi.Parameter(
                name="company",
                in_=openapi.IN_QUERY,
                description="Filter products by company ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Filter products by search",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).top_products(*args, **kwargs)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: ProductDetailSerializer},
        tags=["Product"],
        operation_description="API to get product detail",
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).get_product(*args, **kwargs)


class GlobalSearchView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: GlobalSearchSerializer},
        tags=["GlobalSearch"],
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Filter [products, categories, companies] by search",
                type=openapi.TYPE_STRING,
            )
        ],
        description="API to global search",
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).global_search(*args, **kwargs)
