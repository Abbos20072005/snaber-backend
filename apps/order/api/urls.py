from django.urls import include, path

urlpatterns = [
    path(
        "v1/order/",
        include(
            ("apps.order.api.v1.urls", "order"),
            namespace="order",
        ),
    ),
]
