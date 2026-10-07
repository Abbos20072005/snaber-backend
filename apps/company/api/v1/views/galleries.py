from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.company.api.v1.serializers.galleries import (
    CompanyGalleryCreateUpdateSerializer,
    CompanyGalleryListSerializer,
)
from apps.company.api.v1.services.galleries import (
    CompanyGalleryService,
)
from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller


class CompanyGalleryCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        request_body=CompanyGalleryCreateUpdateSerializer,
        responses={200: CompanyGalleryListSerializer},
        tags=["Gallery"],
        operation_description="Company Gallery  create",
    )
    def post(self, request, *args, **kwargs):
        return CompanyGalleryService(request=request).create_gallery(*args, **kwargs)


class CompanyGalleryListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CompanyGalleryListSerializer},
        tags=["Gallery"],
        operation_description="Company Gallery by company id",
    )
    def get(self, request, *args, **kwargs):
        return CompanyGalleryService(request=request).get_company_gallery(
            *args, **kwargs
        )


class CompanyGalleryDetailUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]
        return [AllowAny()]

    @swagger_auto_schema(
        request_body=CompanyGalleryCreateUpdateSerializer,
        responses={200: CompanyGalleryListSerializer},
        tags=["Gallery"],
        operation_description="Company Gallery update",
    )
    def patch(self, request, *args, **kwargs):
        return CompanyGalleryService(request=request).update_gallery(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CompanyGalleryListSerializer},
        tags=["Gallery"],
        operation_description="Company Gallery delete",
    )
    def delete(self, request, *args, **kwargs):
        return CompanyGalleryService(request=request).delete_gallery(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: CompanyGalleryListSerializer},
        tags=["Gallery"],
        operation_description="Company Gallery detail",
    )
    def get(self, request, *args, **kwargs):
        return CompanyGalleryService(request=request).get_gallery(*args, **kwargs)
