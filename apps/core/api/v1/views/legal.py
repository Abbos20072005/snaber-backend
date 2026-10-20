from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.v1.serializers.legal import (
    LegalClientsInfoListSerializer,
    LegalClientsInfoSerializer,
)
from apps.core.api.v1.services.legal import LegalClientsInfoService
from apps.core.permissions import IsAdmin


class LegalClientsInfoView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdmin()]
        return [AllowAny()]

    @swagger_auto_schema(
        responses={200: LegalClientsInfoListSerializer},
        tags=["LegalClientsInfo"],
        operation_description="Legal clients info get",
    )
    def get(self, request, *args, **kwargs):
        return LegalClientsInfoService(request=request).get_legal_info(
            *args, **kwargs
        )

    @swagger_auto_schema(
        request_body=LegalClientsInfoSerializer,
        responses={200: LegalClientsInfoListSerializer},
        tags=["LegalClientsInfo"],
        operation_description="Legal clients info create",
    )
    def post(self, request, *args, **kwargs):
        return LegalClientsInfoService(request=request).create_legal_info(
            *args, **kwargs
        )
