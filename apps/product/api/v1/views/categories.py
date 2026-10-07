from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin
from apps.product.api.v1.serializers.categories import (
    CategoryBreadcrumbHelperSerializer,
    CategoryCreateSerializer,
    CategoryListSerializer,
    CategoryUpdateSerializer,
)
from apps.product.api.v1.services.categories import CategoryService


class CategoryPublicDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        tags=["Category"],
        operation_description="Public category detail",
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_public_child_categories(
            *args, **kwargs
        )


class CategoriesPublicListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        tags=["Category"],
        operation_description="All public categories list",
        manual_parameters=[
            openapi.Parameter(
                name="is_popular",
                in_=openapi.IN_QUERY,
                description="Filter products by is_popular",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_public_categories(*args, **kwargs)


class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        tags=["Category"],
        operation_description="All not children categories list",
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_categories(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        request_body=CategoryCreateSerializer,
        tags=["Category"],
        operation_description="API to create category",
    )
    def post(self, request, *args, **kwargs):
        return CategoryService(request=request).create_category(*args, **kwargs)


class CategoryChildListUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        tags=["Category"],
        operation_description="All children categories list (according to category ID)",
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_child_categories(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CategoryListSerializer},
        request_body=CategoryUpdateSerializer,
        tags=["Category"],
        operation_description="Category update by ID",
    )
    def patch(self, request, *args, **kwargs):
        return CategoryService(request=request).update_category(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Category"], operation_description="Category delete by ID"
    )
    def delete(self, request, *args, **kwargs):
        return CategoryService(request=request).delete_category(*args, **kwargs)


class CategoryBreadcrumbView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: CategoryBreadcrumbHelperSerializer},
        tags=["Category"],
        operation_description="API to get breadcrumb of "
        "certain category according to its ID",
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_category_breadcrumbs(
            *args, **kwargs
        )


class CategoryPublicBreadcrumbView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CategoryBreadcrumbHelperSerializer},
        tags=["Category"],
        operation_description="API to get active category breadcrumb",
    )
    def get(self, request, *args, **kwargs):
        return CategoryService(request=request).get_public_category_breadcrumbs(
            *args, **kwargs
        )
