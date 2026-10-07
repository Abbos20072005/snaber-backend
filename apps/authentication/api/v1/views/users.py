from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

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
from apps.authentication.api.v1.services.users import UserService
from apps.core.permissions import IsAdminOrSuperAdmin
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


class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserRegisterSerializer,
        responses={201: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Register a new user with phone number and full name."
        " An OTP will be sent for verification.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).register()


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Login a user with phone number.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).login()


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


class UserUpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserUpdatePasswordSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
    )
    def patch(self, request, *args, **kwargs):
        return UserService(request=request).update_password(*args, **kwargs)


class UserUpdateEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=UserUpdateEmailSerializer,
        responses={200: UserUpdateEmailSerializer},
        tags=["User"],
        operation_description="Update an existing user's email address.",
    )
    def patch(self, request, *args, **kwargs):
        return UserService(request=request).update_email(*args, **kwargs)


class UsersListView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

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
    permission_classes = [IsAdminOrSuperAdmin]

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


class ForgetPasswordRequestView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ForgetPasswordRequestSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Send a password reset OTP to the user's email address.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).forget_password_request()


class ForgetPasswordResendView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ForgetPasswordRequestSerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Resend password reset OTP to the user's email address.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).forget_password_resend()


class ForgetPasswordVerifyView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ForgetPasswordVerifySerializer,
        responses={200: ServiceDefaultResponseSerializer},
        tags=["User"],
        operation_description="Verify the OTP and set a new password.",
    )
    def post(self, request, *args, **kwargs):
        return UserService(request=request).forget_password_verify()
