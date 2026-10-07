from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.v1.serializers.faqs import (
    FaqCreateUpdateSerializer,
    FaqListSerializer,
)
from apps.core.api.v1.services.faqs import (
    FaqService,
)
from apps.core.permissions import IsAdminOrSuperAdmin


class FaqCreateListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [AllowAny()]

    @swagger_auto_schema(
        responses={200: FaqListSerializer},
        tags=["Faq"],
        operation_description="Faq list",
    )
    def get(self, request, *args, **kwargs):
        return FaqService(request=request).get_faqs(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: FaqListSerializer},
        request_body=FaqCreateUpdateSerializer,
        tags=["Faq"],
        operation_description="Faq create",
    )
    def post(self, request, *args, **kwargs):
        return FaqService(request=request).create_faq(*args, **kwargs)


class FaqDetailUpdateDeleteView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE"):
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [AllowAny()]

    @swagger_auto_schema(
        responses={200: FaqListSerializer},
        tags=["Faq"],
        operation_description="Faq detail",
    )
    def get(self, request, *args, **kwargs):
        return FaqService(request=request).get_faq(*args, **kwargs)

    @swagger_auto_schema(
        tags=["Faq"],
        operation_description="Faq delete",
    )
    def delete(self, request, *args, **kwargs):
        return FaqService(request=request).delete_faq(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: FaqListSerializer},
        request_body=FaqCreateUpdateSerializer,
        tags=["Faq"],
        operation_description="Faq update",
    )
    def patch(self, request, *args, **kwargs):
        return FaqService(request=request).update_faq(*args, **kwargs)
