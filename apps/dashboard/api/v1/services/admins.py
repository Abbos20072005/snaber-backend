from apps.core.services import BaseService
from apps.dashboard.api.v1.repositories.admins import AdminRepository
from apps.dashboard.api.v1.serializers.admins import (
    Last30DaysStatsSerializer,
    MonthlyRevenueItemSerializer,
    OrdersCountByCategorySerializer,
    TodayOrdersCountSerializer,
    TopProductByOrdersSerializer,
    UserCountsSerializer,
    WeeklyJoinedUsersItemSerializer,
)


class AdminService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = AdminRepository()

    def get_today_orders_count(self, *args, **kwargs):
        data = {
            "orders_count": self.db.get_today_orders_count(),
        }
        return self.get_response_object(
            data, TodayOrdersCountSerializer, context={"request": self.request}
        )

    def get_last_30_days_stats(self, *args, **kwargs):
        data = self.db.get_last_30_days_stats()
        return self.get_response_object(
            data, Last30DaysStatsSerializer, context={"request": self.request}
        )

    def get_user_counts(self, *args, **kwargs):
        data = self.db.get_user_counts()
        return self.get_response_object(
            data, UserCountsSerializer, context={"request": self.request}
        )

    def get_current_week_joined_users(self, *args, **kwargs):
        data = self.db.get_current_week_joined_users()
        return self.get_response(
            data,
            WeeklyJoinedUsersItemSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_orders_count_by_category(self, *args, **kwargs):
        data = self.db.get_orders_count_by_category()
        return self.get_response(
            data,
            OrdersCountByCategorySerializer,
            many=True,
            context={"request": self.request},
        )

    def get_top_products_by_orders(self, *args, **kwargs):
        data = self.db.get_top_products_by_orders()
        return self.get_response(
            data,
            TopProductByOrdersSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_monthly_revenue_stats(self, *args, **kwargs):
        data = self.db.get_monthly_revenue_stats()
        return self.get_response(
            data,
            MonthlyRevenueItemSerializer,
            many=True,
            context={"request": self.request},
        )
