from apps.authentication.api.v1.repositories.otp import OTPRepository
from apps.authentication.api.v1.serializers.otp import (
    OTPResendSerializer,
    OTPSerializer,
)
from apps.authentication.api.v1.services.user_manager import UserManager
from apps.authentication.api.v1.utils.otp import send_verification_email, verify_code
from apps.authentication.models import User
from apps.core.exceptions import ObjectNotFoundException, ValidationError
from apps.core.services import BaseService
from apps.notification.api.v1.repositories.notifications import NotificationRepository
from apps.notification.models import Notification


class OTPService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = OTPRepository

    def verify(self, *args, **kwargs):
        serializer = OTPSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp_code = serializer.validated_data.get("otp_code")

        is_valid = verify_code(email, otp_code)

        if not is_valid:
            raise ValidationError(message="Invalid or expired OTP code.")

        user = User.objects.filter(email=email).first()
        if not user:
            raise ObjectNotFoundException(
                message="User not found or already verified",
                message_key="user_not_found_or_already_verified",
            )

        user.is_verified = True
        user.save(update_fields=["is_verified"])

        NotificationRepository().create_notification(
            user=user,
            title_uz="Email tasdiqlandi",
            title_ru="Электронная почта подтверждена",
            title_en="Email Verified",
            message_uz="Email manzilingiz muvaffaqiyatli tasdiqlandi. B2B Market'ga xush kelibsiz!",
            message_ru="Ваш адрес электронной почты успешно подтвержден. Добро пожаловать в B2B Market!",
            message_en="Your email has been successfully verified. Welcome to B2B Market!",
            notification_type=Notification.NotificationType.OTHER,
        )

        token = UserManager.get_tokens_for_user(user)

        return self.get_response_object(
            obj={"result": token},
            context={"request": self.request},
        )

    def resend(self, *args, **kwargs):
        serializer = OTPResendSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        user = User.objects.filter(email=email, is_verified=False).first()

        if not user:
            raise ObjectNotFoundException(
                message="User not found or already verified",
                message_key="user_not_found_or_already_verified",
            )

        send_verification_email(email)

        return self.get_response_object(
            obj={"result": "OTP code was resent to the user"},
            context={"request": self.request},
        )

    def verify_email(self, *args, **kwargs):
        user = self.request.user
        serializer = OTPSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        otp_code = serializer.validated_data.get("otp_code")

        is_valid = verify_code(email, otp_code)

        if not is_valid:
            raise ValidationError(message="Invalid or expired OTP code.")

        user.email = email
        user.save(update_fields=["email"])

        return self.get_response_object(
            obj={"result": "New email verified"},
            context={"request": self.request},
        )
