from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin, IsSeller
from apps.product.api.v1.serializers.units import (
    UnitCreateSerializer,
    UnitListSerializer,
)
from apps.product.api.v1.services.units import UnitService


class UnitListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [IsAuthenticated(), (IsSeller | IsAdminOrSuperAdmin)()]

    @swagger_auto_schema(
        responses={200: UnitListSerializer},
        tags=["Unit"],
        operation_description="Unit list",
        manual_parameters=[
            openapi.Parameter(
                name="unit",
                in_=openapi.IN_QUERY,
                description="Filter units by unit",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return UnitService(request=request).get_units(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: UnitListSerializer},
        request_body=UnitCreateSerializer,
        tags=["Unit"],
        operation_description="Unit create",
    )
    def post(self, request, *args, **kwargs):
        return UnitService(request=request).create_unit(*args, **kwargs)


class UnitUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: UnitListSerializer},
        request_body=UnitCreateSerializer,
        tags=["Unit"],
        operation_description="Unit update",
    )
    def patch(self, request, *args, **kwargs):
        return UnitService(request=request).update_unit(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Unit"],
        operation_description="Unit delete",
    )
    def delete(self, request, *args, **kwargs):
        return UnitService(request=request).delete_unit(*args, **kwargs)
