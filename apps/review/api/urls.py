from django.urls import include, path

urlpatterns = [
    path(
        "v1/review/",
        include(
            ("apps.review.api.v1.urls", "review"),
            namespace="review",
        ),
    ),
]
