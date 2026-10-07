from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.company.api.v1.serializers.certificates import (
    CompanyCertificateCreateUpdateSerializer,
    CompanyCertificateListSerializer,
)
from apps.company.api.v1.services.certificates import (
    CompanyCertificateService,
)
from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller


class CompanyCertificateCreateView(APIView):
    permission_classes = [IsAuthenticated, IsSeller | IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        request_body=CompanyCertificateCreateUpdateSerializer,
        responses={200: CompanyCertificateListSerializer},
        tags=["Certificate"],
        operation_description="Company Certificate create",
    )
    def post(self, request, *args, **kwargs):
        return CompanyCertificateService(request=request).create_certificate(
            *args, **kwargs
        )


class CompanyCertificateListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CompanyCertificateListSerializer},
        tags=["Certificate"],
        operation_description="Company Certificate by company id",
    )
    def get(self, request, *args, **kwargs):
        return CompanyCertificateService(request=request).get_company_certificate(
            *args, **kwargs
        )


class CompanyCertificateDetailUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]
        return [AllowAny()]

    @swagger_auto_schema(
        request_body=CompanyCertificateCreateUpdateSerializer,
        responses={200: CompanyCertificateListSerializer},
        tags=["Certificate"],
        operation_description="Company Certificate update",
    )
    def patch(self, request, *args, **kwargs):
        return CompanyCertificateService(request=request).update_certificate(
            *args, **kwargs
        )

    @swagger_auto_schema(
        responses={200: CompanyCertificateListSerializer},
        tags=["Certificate"],
        operation_description="Company Certificate delete",
    )
    def delete(self, request, *args, **kwargs):
        return CompanyCertificateService(request=request).delete_certificate(
            *args, **kwargs
        )

    @swagger_auto_schema(
        responses={200: CompanyCertificateListSerializer},
        tags=["Certificate"],
        operation_description="Company Certificate detail",
    )
    def get(self, request, *args, **kwargs):
        return CompanyCertificateService(request=request).get_certificate(
            *args, **kwargs
        )
