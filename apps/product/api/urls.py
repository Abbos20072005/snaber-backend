from django.urls import include, path

urlpatterns = [
    path(
        "v1/product/",
        include(
            ("apps.product.api.v1.urls", "product"),
            namespace="product",
        ),
    ),
]
