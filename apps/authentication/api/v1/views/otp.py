from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.authentication.api.v1.serializers.otp import (
    OTPSendSerializer,
    OTPVerifySerializer,
)
from apps.authentication.api.v1.services.otp import OTPService
from apps.core.services import ServiceDefaultResponseSerializer


class OTPSendView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OTPSendSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Send a one-time code to the phone number."
        " Also used to resend the code once the cooldown has passed.",
    )
    def post(self, request, *args, **kwargs):
        return OTPService(request=request).send()


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=OTPVerifySerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Verify the code and log in."
        " A new buyer account is created for an unknown phone number.",
    )
    def post(self, request, *args, **kwargs):
        return OTPService(request=request).verify()
