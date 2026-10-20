from django.urls import path

from apps.order.api.v1.views.buyer import BuyerOrderView
from apps.order.api.v1.views.order import (
    # OrderConversationView,
    OrderDetailView,
    OrderListView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    # Chat center (order conversation) is disabled for the frontend
    # path(
    #     "<int:pk>/conversation/",
    #     OrderConversationView.as_view(),
    #     name="order-conversation",
    # ),
    path("buyers/<int:pk>/", BuyerOrderView.as_view(), name="buyer-order"),
]

