from django.urls import path

from apps.orders.api.v1.views import OrderCreateAPIView

urlpatterns = [
    # order
    path("", OrderCreateAPIView.as_view(), name="order-create"),
]
