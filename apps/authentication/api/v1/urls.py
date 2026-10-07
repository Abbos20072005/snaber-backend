from django.urls import path

from apps.authentication.api.v1 import views

urlpatterns = [
    path("users/register/", views.UserRegisterView.as_view(), name="users-register"),
    path("users/otp/verify/", views.OTPVerifyView.as_view(), name="users-otp-verify"),
    path("users/login/", views.UserLoginView.as_view(), name="users-login"),
    path("users/oauth/google/", views.GoogleLoginView.as_view(), name="google_login"),
    path("users/otp/resend/", views.OTPResendView.as_view(), name="users-otp-resend"),
    path("users/me/", views.UserMeView.as_view(), name="users-me"),
    path(
        "users/token-refresh/",
        views.UserRefreshTokenView.as_view(),
        name="users-token-refresh",
    ),
    path("users/update/", views.UserUpdateView.as_view(), name="users-update"),
    path(
        "users/update/password/",
        views.UserUpdatePasswordView.as_view(),
        name="users-update-password",
    ),
    path("users/email/", views.UserUpdateEmailView.as_view(), name="users-email"),
    path(
        "users/otp/verify/email/",
        views.OTPVerifyEmailView.as_view(),
        name="users-verify-email",
    ),
    path("users/", views.UsersListView.as_view(), name="users-list"),
    path(
        "users/<int:pk>/",
        views.UsersDetailUpdateDeleteView.as_view(),
        name="users-detail",
    ),
    path(
        "users/forget-password/",
        views.ForgetPasswordRequestView.as_view(),
        name="users-forget-password",
    ),
    path(
        "users/forget-password/resend/",
        views.ForgetPasswordResendView.as_view(),
        name="users-forget-password-resend",
    ),
    path(
        "users/forget-password/verify/",
        views.ForgetPasswordVerifyView.as_view(),
        name="users-forget-password-verify",
    ),
]
