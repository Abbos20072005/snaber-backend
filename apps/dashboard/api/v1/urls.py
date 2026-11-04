from django.urls import path

from apps.dashboard.api.v1.views.admins import (
    CurrentWeekJoinedUsersAPIView,
    MonthlyRevenueStatsAPIView,
    OrdersCountByCategoryAPIView,
    TodayOrdersCountAPIView,
    TopProductsByOrdersAPIView,
    UserCountsAPIView,
)
from apps.dashboard.api.v1.views.buyers import (
    BuyerKpiAPIView,
    BuyerPurchaseMomentumAPIView,
    BuyerRecentBuyingActivityAPIView,
)
from apps.dashboard.api.v1.views.insights import (
    AbandonedCartsAPIView,
    OverviewAPIView,
    StockAlertsAPIView,
)

urlpatterns = [
    path(
        "admins/today-orders/",
        TodayOrdersCountAPIView.as_view(),
        name="admin-today-orders",
    ),
    path(
        "admins/monthly-revenue/",
        MonthlyRevenueStatsAPIView.as_view(),
        name="admin-monthly-revenue",
    ),
    path(
        "admins/user-counts/",
        UserCountsAPIView.as_view(),
        name="admin-user-counts",
    ),
    path(
        "admins/weekly-joined-users/",
        CurrentWeekJoinedUsersAPIView.as_view(),
        name="admin-weekly-joined-users",
    ),
    path(
        "admins/top-products/",
        TopProductsByOrdersAPIView.as_view(),
        name="admin-top-products",
    ),
    path(
        "admins/orders-by-category/",
        OrdersCountByCategoryAPIView.as_view(),
        name="admin-orders-by-category",
    ),
    path("admins/overview/", OverviewAPIView.as_view(), name="admin-overview"),
    path(
        "admins/abandoned-carts/",
        AbandonedCartsAPIView.as_view(),
        name="admin-abandoned-carts",
    ),
    path(
        "admins/stock-alerts/",
        StockAlertsAPIView.as_view(),
        name="admin-stock-alerts",
    ),
    # Chat center (buyer engagement chart) is disabled for the frontend
    # path(
    #     "sellers/buyer-engagement/",
    #     SellerBuyerEngagementAPIView.as_view(),
    #     name="seller-dashboard-buyer-engagement",
    # ),
    path(
        "buyers/kpis/",
        BuyerKpiAPIView.as_view(),
        name="buyer-dashboard-kpis",
    ),
    path(
        "buyers/purchase-momentum/",
        BuyerPurchaseMomentumAPIView.as_view(),
        name="buyer-dashboard-purchase-momentum",
    ),
    path(
        "buyers/recent-buying-activity/",
        BuyerRecentBuyingActivityAPIView.as_view(),
        name="buyer-dashboard-recent-buying-activity",
    ),
]
