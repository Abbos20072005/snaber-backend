from django.urls import path

from apps.dashboard.api.v1.views.admins import (
    CurrentWeekJoinedUsersAPIView,
    Last30DaysStatsAPIView,
    MonthlyRevenueStatsAPIView,
    OrdersCountByCategoryAPIView,
    RFQOrderStatusCountAPIView,
    TodayOrdersCountAPIView,
    TopCompaniesByOrdersAPIView,
    UserCountsAPIView,
)
from apps.dashboard.api.v1.views.buyers import (
    BuyerSummaryAPIView,
    BuyerRecentBuyingActivityAPIView,
    BuyerOrderTypeSplitAPIView,
    BuyerStatusMixAPIView,
    BuyerPurchaseMomentumAPIView,
    BuyerKpiAPIView,
)
from apps.dashboard.api.v1.views.sellers import (
    # SellerBuyerEngagementAPIView,
    SellerHeroAPIView,
    SellerKPIsAPIView,
    SellerRecentOrdersAPIView,
    SellerRevenueMomentumAPIView,
    SellerRFQPipelineAPIView,
    SellerSalesByCategoryAPIView,
    SellerTopProductsAPIView,
)

urlpatterns = [
    path(
        "admins/today-orders/",
        TodayOrdersCountAPIView.as_view(),
        name="admin-today-orders",
    ),
    path(
        "admins/last-30-days-stats/",
        Last30DaysStatsAPIView.as_view(),
        name="admin-last-30-days-stats",
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
        "admins/rfq-orders-by-status/",
        RFQOrderStatusCountAPIView.as_view(),
        name="admin-rfq-orders-by-status",
    ),
    path(
        "admins/weekly-joined-users/",
        CurrentWeekJoinedUsersAPIView.as_view(),
        name="admin-weekly-joined-users",
    ),
    path(
        "admins/top-companies/",
        TopCompaniesByOrdersAPIView.as_view(),
        name="admin-top-companies",
    ),
    path(
        "admins/orders-by-category/",
        OrdersCountByCategoryAPIView.as_view(),
        name="admin-orders-by-category",
    ),
    path(
        "sellers/hero-summary/",
        SellerHeroAPIView.as_view(),
        name="seller-dashboard-hero-summary",
    ),
    path(
        "sellers/kpis/",
        SellerKPIsAPIView.as_view(),
        name="seller-dashboard-kpis",
    ),
    path(
        "sellers/revenue-momentum/",
        SellerRevenueMomentumAPIView.as_view(),
        name="seller-dashboard-revenue-momentum",
    ),
    path(
        "sellers/sales-by-category/",
        SellerSalesByCategoryAPIView.as_view(),
        name="seller-dashboard-sales-by-category",
    ),
    # Chat center (buyer engagement chart) is disabled for the frontend
    # path(
    #     "sellers/buyer-engagement/",
    #     SellerBuyerEngagementAPIView.as_view(),
    #     name="seller-dashboard-buyer-engagement",
    # ),
    path(
        "sellers/rfq-pipeline/",
        SellerRFQPipelineAPIView.as_view(),
        name="seller-dashboard-rfq-pipeline",
    ),
    path(
        "sellers/top-products/",
        SellerTopProductsAPIView.as_view(),
        name="seller-dashboard-top-products",
    ),
    path(
        "sellers/recent-orders/",
        SellerRecentOrdersAPIView.as_view(),
        name="seller-dashboard-recent-orders",
    ),
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
        "buyers/status-mix/",
        BuyerStatusMixAPIView.as_view(),
        name="buyer-dashboard-status-mix",
    ),
    path(
        "buyers/order-type-split/",
        BuyerOrderTypeSplitAPIView.as_view(),
        name="buyer-dashboard-order-type-split",
    ),
    path(
        "buyers/recent-buying-activity/",
        BuyerRecentBuyingActivityAPIView.as_view(),
        name="buyer-dashboard-recent-buying-activity",
    ),
    path(
        "buyers/summary/",
        BuyerSummaryAPIView.as_view(),
        name="buyer-dashboard-summary",
    ),
]

