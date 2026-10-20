"""
URL configuration for config project.
"""

import re

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

admin.site.site_header = "Snaber boshqaruv paneli"
admin.site.site_title = "Snaber"
admin.site.index_title = "Boshqaruv"

urlpatterns = [
    path("admin/", admin.site.urls),
    # API v1 endpoints
    path("api/v1/catalog/", include("apps.catalog.api.v1.urls")),
    path("api/v1/orders/", include("apps.orders.api.v1.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Media DEBUG=False da ham beriladi. Prod'da nginx `/media/` ni o'ziga olsa,
# bu yo'nalishga so'rov yetib kelmaydi.
urlpatterns += [
    re_path(
        rf"^{re.escape(settings.MEDIA_URL.lstrip('/'))}(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
