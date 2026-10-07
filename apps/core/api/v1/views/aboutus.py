from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.api.v1.serializers.aboutus import (
    AboutUsImageSerializer,
    AboutUsListSerializer,
    AboutUsSerializer,
)
from apps.core.api.v1.services.aboutus import AboutUsImagesService, AboutUsService
from apps.core.permissions import IsAdminOrSuperAdmin


class AboutUsView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminOrSuperAdmin()]
        return [AllowAny()]

    @swagger_auto_schema(
        responses={200: AboutUsListSerializer},
        tags=["AboutUs"],
        operation_description="About Us get",
    )
    def get(self, request, *args, **kwargs):
        return AboutUsService(request=request).get_about_us(*args, **kwargs)

    @swagger_auto_schema(
        request_body=AboutUsSerializer,
        responses={200: AboutUsListSerializer},
        tags=["AboutUs"],
        operation_description="About Us create",
    )
    def post(self, request, *args, **kwargs):
        return AboutUsService(request=request).create_about_us(*args, **kwargs)


class AboutUsImageView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        request_body=AboutUsImageSerializer,
        responses={200: AboutUsImageSerializer},
        tags=["AboutUs"],
        operation_description="About Us Images create",
    )
    def post(self, request, *args, **kwargs):
        return AboutUsImagesService(request=request).create_about_us_image(
            *args, **kwargs
        )
