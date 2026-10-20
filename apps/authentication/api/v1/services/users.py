from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.api.v1.filters.users import UserFilter
from apps.authentication.api.v1.repositories.users import UserRepository
from apps.authentication.api.v1.serializers.users import (
    UserMeSerializer,
    UserRefreshTokenSerializer,
    UsersSerializers,
    UserUpdateSerializer,
    UserUpdateSerializers,
)
from apps.authentication.models import User
from apps.core.exceptions import (
    InvalidAuthCredentialsException,
    PermissionDeniedException,
)
from apps.core.services import BaseService


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
