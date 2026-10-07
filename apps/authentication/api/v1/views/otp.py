from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.authentication.api.v1.serializers.otp import (
    OTPResendSerializer,
    OTPSerializer,
)
from apps.authentication.api.v1.services.otp import OTPService
from apps.core.services import ServiceDefaultResponseSerializer


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OTPSerializer,
        responses={201: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Verify the OTP sent to the user's email."
        " This endpoint should be called after registration to verify"
        " the user's email with otp.",
    )
    def post(self, request, *args, **kwargs):
        return OTPService(request=request).verify()


class OTPResendView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OTPResendSerializer,
        responses={201: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Resend OTP to the user's phone number.",
    )
    def post(self, request, *args, **kwargs):
        return OTPService(request=request).resend()


class OTPVerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=OTPSerializer,
        responses={201: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Verify the OTP sent to the user's email."
        " This endpoint should be called after update email to verify"
        " the user's email with otp.",
    )
    def post(self, request, *args, **kwargs):
        return OTPService(request=request).verify_email()
