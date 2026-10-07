from django.urls import include, path

urlpatterns = [
    path(
        "v1/notifications/",
        include(
            ("apps.notification.api.v1.urls", "notifications"),
            namespace="notifications",
        ),
    ),
]
