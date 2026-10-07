from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.api.v1.filters.users import UserFilter
from apps.authentication.api.v1.repositories.users import UserRepository
from apps.authentication.api.v1.serializers.users import (
    ForgetPasswordRequestSerializer,
    ForgetPasswordVerifySerializer,
    UserLoginSerializer,
    UserMeSerializer,
    UserRefreshTokenSerializer,
    UserRegisterSerializer,
    UsersSerializers,
    UserUpdateEmailSerializer,
    UserUpdatePasswordSerializer,
    UserUpdateSerializer,
    UserUpdateSerializers,
)
from apps.authentication.api.v1.services.user_manager import UserManager
from apps.authentication.api.v1.utils.otp import (
    send_forget_password_email,
    send_verification_email,
    verify_forget_password_code,
)
from apps.authentication.models import User
from apps.core.exceptions import (
    InvalidAuthCredentialsException,
    ObjectNotFoundException,
    PermissionDeniedException,
    UserAlreadyExistsException,
    ValidationError,
)
from apps.core.services import BaseService
from apps.product.utils import merge_session_to_db, merge_session_to_db_cart


class UserService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = UserRepository()

    def me(self, *args, **kwargs):
        return self.get_response_object(
            obj=self.request.user,
            response_serializer_class=UserMeSerializer,
            context={"request": self.request},
        )

    def login(self, *args, **kwargs):
        serializer_class = UserLoginSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer_class.is_valid(raise_exception=True)

        user = serializer_class.validated_data.get("user")
        token = UserManager.get_tokens_for_user(user)
        merge_session_to_db(user, request=self.request)
        merge_session_to_db_cart(user, request=self.request)

        return self.get_response_object(
            obj={
                "result": token,
            },
            context={"request": self.request},
        )

    def register(self, *args, **kwargs):
        serializer = UserRegisterSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")

        if User.objects.filter(email=email, is_verified=True).exists():
            raise UserAlreadyExistsException()

        user = User.objects.filter(email=email, is_verified=False).first()
        if not user:
            serializer.save(is_verified=False)

        send_verification_email(email)

        return self.get_response_object(
            obj={"result": "OTP code was sent to the user"},
            context={"request": self.request},
        )

    def refresh_token(self, *args, **kwargs):
        serializer = UserRefreshTokenSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data.get("refresh_token")

        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()

            user_id = refresh.payload.get("user_id")
            user = User.objects.get(id=user_id)

            new_refresh = RefreshToken.for_user(user)
            new_access_token = str(new_refresh.access_token)
            new_refresh_token = str(new_refresh)

            return self.get_response_object(
                obj={
                    "result": {
                        "access_token": new_access_token,
                        "refresh_token": new_refresh_token,
                    },
                },
                context={"request": self.request},
            )

        except TokenError:
            raise InvalidAuthCredentialsException(
                message="Invalid refresh token."
            ) from None

    from rest_framework.exceptions import ValidationError

    def update_user(self, *args, **kwargs):
        serializer = UserUpdateSerializer(
            self.request.user,
            data=self.request.data,
            partial=True,
            context={"request": self.request},
        )
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        serializer.save()
        return self.get_response_object(
            serializer.data, UserUpdateSerializer, context={"request": self.request}
        )

    def update_password(self, *args, **kwargs):
        user = self.request.user
        serializer = UserUpdatePasswordSerializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return self.get_response_object(
            obj={
                "result": {
                    "id": user.id,
                },
                "ok": True,
            }
        )

    def update_email(self, *args, **kwargs):
        user = self.request.user
        serializer = UserUpdateEmailSerializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        send_verification_email(email)

        return self.get_response_object(
            obj={
                "result": {
                    "id": user.id,
                },
                "ok": True,
            }
        )

    def get_users(self, *args, **kwargs):
        users = self.db.get_users()
        users = UserFilter(self.request.query_params, queryset=users).qs
        return self.get_paginated_response(
            users, UsersSerializers, context={"request": self.request}
        )

    def get_user(self, *args, **kwargs):
        user = self.db.get_user(user_id=kwargs.get("pk"))
        return self.get_response_object(
            user,
            UsersSerializers,
            context={"request": self.request},
        )

    def user_update(self, *args, **kwargs):
        user = self.db.get_user(user_id=kwargs.get("pk"))
        if self.request.user.role == User.Roles.ADMIN and user.role in [
            User.Roles.ADMIN
        ]:
            raise PermissionDeniedException(
                message="Admins cannot update other admins",
                message_key="cannot_update_admin",
            )

        serializer = UserUpdateSerializers(
            instance=user,
            data=self.request.data,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.get_response_object(
            serializer.instance,
            UsersSerializers,
            context={"request": self.request},
        )

    def user_delete(self, *args, **kwargs):
        user = self.db.get_user(user_id=kwargs.get("pk"))
        if self.request.user.role == User.Roles.ADMIN and user.role in [
            User.Roles.ADMIN
        ]:
            raise PermissionDeniedException(
                message="Admins cannot delete other admins",
                message_key="cannot_delete_admin",
            )
        user.delete()
        return self.get_response_object(
            obj={"result": "User deleted"},
        )

    def forget_password_request(self, *args, **kwargs):
        serializer = ForgetPasswordRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email, is_verified=True).first()
        if not user:
            raise ObjectNotFoundException(
                message="No verified account found with this email",
                message_key="user_not_found",
            )

        send_forget_password_email(email)

        return self.get_response_object(
            obj={"result": "Password reset code was sent to your email"},
        )

    def forget_password_resend(self, *args, **kwargs):
        serializer = ForgetPasswordRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email, is_verified=True).first()
        if not user:
            raise ObjectNotFoundException(
                message="No verified account found with this email",
                message_key="user_not_found",
            )

        send_forget_password_email(email)

        return self.get_response_object(
            obj={"result": "Password reset code was resent to your email"},
        )

    def forget_password_verify(self, *args, **kwargs):
        serializer = ForgetPasswordVerifySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp_code"]
        new_password = serializer.validated_data["new_password"]

        if not verify_forget_password_code(email, otp_code):
            raise ValidationError(message="Invalid or expired OTP code.")

        user = User.objects.filter(email=email, is_verified=True).first()
        if not user:
            raise ObjectNotFoundException(
                message="User not found",
                message_key="user_not_found",
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return self.get_response_object(
            obj={"result": "Password has been reset successfully"},
        )
