from django.urls import include, path

urlpatterns = [
    path(
        "v1/dashboards/",
        include(
            ("apps.dashboard.api.v1.urls", "dashboards"),
            namespace="dashboards",
        ),
    ),
]
