from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.authentication.api.v1.serializers.users import (
    UserMeSerializer,
    UserRefreshTokenSerializer,
    UsersSerializers,
    UserUpdateSerializer,
    UserUpdateSerializers,
)
from apps.authentication.api.v1.services.users import UserService
from apps.core.permissions import IsAdmin
from apps.core.services import ServiceDefaultResponseSerializer


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserMeSerializer},
        tags=["User"],
        operation_description="User me information",
    )
    def get(self, request, *args, **kwargs):
        return UserService(request=request).me()


class UserRefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={201: ServiceDefaultResponseSerializer},
        request_body=UserRefreshTokenSerializer,
        tags=["User"],
        operation_description="Refresh access and refresh tokens using"
        "a valid refresh token."
        "The old refresh token will be blacklisted and cannot be used again.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).refresh_token(*args, **kwargs)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
    )
    def patch(self, request, *args, **kwargs):
        return UserService(request=request).update_user(*args, **kwargs)


class UsersListView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        responses={200: UsersSerializers},
        tags=["User"],
        operation_description="List all users",
        manual_parameters=[
            openapi.Parameter(
                "role",
                openapi.IN_QUERY,
                description="Filter users by role",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return UserService(request=request).get_users()


class UsersDetailUpdateDeleteView(APIView):
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        responses={200: UsersSerializers},
        tags=["User"],
        operation_description="user details",
    )
    def get(self, request, *args, **kwargs):
        return UserService(request=request).get_user(*args, **kwargs)

    @swagger_auto_schema(
        request_body=UserUpdateSerializers,
        responses={200: UsersSerializers},
        tags=["User"],
        operation_description="user update",
    )
    def patch(self, request, *args, **kwargs):
        return UserService(request=request).user_update(*args, **kwargs)

    @swagger_auto_schema(
        responses={200: UsersSerializers},
        tags=["User"],
        operation_description="User delete",
    )
    def delete(self, request, *args, **kwargs):
        return UserService(request=request).user_delete(*args, **kwargs)
