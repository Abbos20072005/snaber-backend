from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.product.api.v1.serializers.products import (
    GlobalSearchSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductImageUploadSerializer,
    ProductListSerializer,
)
from apps.product.api.v1.services.products import ProductService

LIST_FILTER_PARAMETERS = [
    openapi.Parameter(
        name="search",
        in_=openapi.IN_QUERY,
        description="Search by product name or SKU",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        name="category",
        in_=openapi.IN_QUERY,
        description="Filter products by category ID (includes sub-categories)",
        type=openapi.TYPE_INTEGER,
    ),
    openapi.Parameter(
        name="price_min",
        in_=openapi.IN_QUERY,
        description="Minimum price",
        type=openapi.TYPE_NUMBER,
    ),
    openapi.Parameter(
        name="price_max",
        in_=openapi.IN_QUERY,
        description="Maximum price",
        type=openapi.TYPE_NUMBER,
    ),
]


class ProductListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=["Product"],
        operation_description="API to get all products (including inactive)",
        manual_parameters=LIST_FILTER_PARAMETERS
        + [
            openapi.Parameter(
                name="is_active",
                in_=openapi.IN_QUERY,
                description="Filter products by is_active",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                name="in_stock",
                in_=openapi.IN_QUERY,
                description="Filter products by availability",
                type=openapi.TYPE_BOOLEAN,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).get_products(*args, **kwargs)

    @swagger_auto_schema(
        responses={201: ProductDetailSerializer},
        request_body=ProductCreateUpdateSerializer,
        tags=["Product"],
        operation_description="API to create product",
    )
    def post(self, request, *args, **kwargs):
        return ProductService(request=request).create_product(*args, **kwargs)


class ProductDetailUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        responses={200: ProductDetailSerializer},
        tags=["Product"],
        operation_description="API to get certain product",
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).get_product(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: ProductDetailSerializer},
        request_body=ProductCreateUpdateSerializer,
        tags=["Product"],
        operation_description="API to update certain product",
    )
    def patch(self, request, *args, **kwargs):
        return ProductService(request=request).update_product(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Product"],
        operation_description="API to delete certain product",
    )
    def delete(self, request, *args, **kwargs):
        return ProductService(request=request).delete_product(*args, **kwargs)


class ProductImageView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @swagger_auto_schema(
        responses={201: ProductImageSerializer(many=True)},
        request_body=ProductImageUploadSerializer,
        tags=["Product"],
        operation_description="API to upload product images (multipart `files`)",
    )
    def post(self, request, *args, **kwargs):
        return ProductService(request=request).upload_images(*args, **kwargs)


class ProductImageDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        tags=["Product"],
        operation_description="API to delete product image",
    )
    def delete(self, request, *args, **kwargs):
        return ProductService(request=request).delete_image(*args, **kwargs)


class ProductTopView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: ProductListSerializer(many=True)},
        tags=["Product"],
        operation_description="API to get public products",
        manual_parameters=LIST_FILTER_PARAMETERS
        + [
            openapi.Parameter(
                name="is_popular",
                in_=openapi.IN_QUERY,
                description="Order products by number of orders",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                name="values",
                in_=openapi.IN_QUERY,
                description="Filter products by attribute value IDs",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
            ),
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
        return ProductService(request=request).get_public_product(*args, **kwargs)


class GlobalSearchView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: GlobalSearchSerializer},
        tags=["GlobalSearch"],
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                description="Filter [products, categories] by search",
                type=openapi.TYPE_STRING,
            )
        ],
        description="API to global search",
    )
    def get(self, request, *args, **kwargs):
        return ProductService(request=request).global_search(*args, **kwargs)
