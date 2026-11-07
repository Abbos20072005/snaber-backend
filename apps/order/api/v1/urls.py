from django.urls import path

from apps.order.api.v1.views.buyer import BuyerOrderView
from apps.order.api.v1.views.order import (
    OrderCustomItemPriceView,
    # OrderConversationView,
    OrderDetailView,
    OrderListView,
    OrderReorderView,
)
from apps.order.api.v1.views.product_request import (
    ProductRequestDetailView,
    ProductRequestListView,
    WantedProductListView,
)

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("requests/", ProductRequestListView.as_view(), name="product-request-list"),
    path(
        "requests/wanted/", WantedProductListView.as_view(), name="wanted-product-list"
    ),
    path(
        "requests/<int:pk>/",
        ProductRequestDetailView.as_view(),
        name="product-request-detail",
    ),
    path(
        "custom-items/<int:pk>/",
        OrderCustomItemPriceView.as_view(),
        name="order-custom-item-price",
    ),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/reorder/", OrderReorderView.as_view(), name="order-reorder"),
    # Chat center (order conversation) is disabled for the frontend
    # path(
    #     "<int:pk>/conversation/",
    #     OrderConversationView.as_view(),
    #     name="order-conversation",
    # ),
    path("buyers/<int:pk>/", BuyerOrderView.as_view(), name="buyer-order"),
]
