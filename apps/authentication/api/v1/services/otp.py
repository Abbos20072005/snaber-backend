import uuid

from django.conf import settings

from apps.authentication.api.v1.serializers.otp import (
    OTPSendSerializer,
    OTPVerifySerializer,
)
from apps.authentication.api.v1.services.user_manager import UserManager
from apps.authentication.api.v1.utils.otp import send_otp, verify_otp
from apps.authentication.models import User
from apps.core.exceptions import PermissionDeniedException
from apps.core.services import BaseService
from apps.product.utils import merge_session_to_db, merge_session_to_db_cart


class OTPService(BaseService):
    def send(self, *args, **kwargs):
        serializer = OTPSendSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        resend_after = send_otp(serializer.validated_data["phone_number"])

        return self.get_response_object(
            obj={
                "result": {
                    "expires_in": settings.OTP_EXPIRY,
                    "resend_after": resend_after,
                }
            },
            context={"request": self.request},
        )

    def verify(self, *args, **kwargs):
        serializer = OTPVerifySerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        verify_otp(phone, serializer.validated_data["otp_code"])

        user = User.objects.filter(phone_number=phone).first()
        is_new_user = user is None
        if is_new_user:
            user = User.objects.create_user(
                username=str(uuid.uuid4()), phone_number=phone, is_verified=True
            )
        elif user.is_blocked or not user.is_active:
            raise PermissionDeniedException(
                message="Your account is blocked.", message_key="user_blocked"
            )
        elif not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        merge_session_to_db(user, request=self.request)
        merge_session_to_db_cart(user, request=self.request)

        return self.get_response_object(
            obj={
                "result": {
                    **UserManager.get_tokens_for_user(user),
                    "is_new_user": is_new_user,
                }
            },
            context={"request": self.request},
        )
