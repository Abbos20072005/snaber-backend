from django.urls import path

from apps.authentication.api.v1 import views

urlpatterns = [
    path("users/otp/send/", views.OTPSendView.as_view(), name="users-otp-send"),
    path("users/otp/verify/", views.OTPVerifyView.as_view(), name="users-otp-verify"),
    path("users/me/", views.UserMeView.as_view(), name="users-me"),
    path(
        "users/token-refresh/",
        views.UserRefreshTokenView.as_view(),
        name="users-token-refresh",
    ),
    path("users/update/", views.UserUpdateView.as_view(), name="users-update"),
    path("users/", views.UsersListView.as_view(), name="users-list"),
    path(
        "users/<int:pk>/",
        views.UsersDetailUpdateDeleteView.as_view(),
        name="users-detail",
    ),
]
