from django.urls import include, path

urlpatterns = [
    path(
        "v1/company/",
        include(
            ("apps.company.api.v1.urls", "company"),
            namespace="company",
        ),
    ),
]
