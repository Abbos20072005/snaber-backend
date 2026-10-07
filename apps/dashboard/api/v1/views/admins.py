from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrSuperAdmin
from apps.dashboard.api.v1.serializers.admins import (
    Last30DaysStatsSerializer,
    MonthlyRevenueItemSerializer,
    OrdersCountByCategorySerializer,
    RFQOrderStatusCountSerializer,
    TodayOrdersCountSerializer,
    TopCompanyByOrdersSerializer,
    UserCountsSerializer,
    WeeklyJoinedUsersItemSerializer,
)
from apps.dashboard.api.v1.services.admins import AdminService


class TodayOrdersCountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: TodayOrdersCountSerializer()},
        tags=["Dashboard"],
        operation_description="Returns today's order count and RFQ order count",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_today_orders_count(*args, **kwargs)


class Last30DaysStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: Last30DaysStatsSerializer()},
        tags=["Dashboard"],
        operation_description="Returns last 30 days stats: total money "
        "spent, total orders count, verified sellers count, total users count",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_last_30_days_stats(*args, **kwargs)


class UserCountsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: UserCountsSerializer()},
        tags=["Dashboard"],
        operation_description="Returns count of sellers, buyers, and total users. "
        "Admins also see moderators count. Super admins additionally see admins count.",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_user_counts()


class CurrentWeekJoinedUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: WeeklyJoinedUsersItemSerializer(many=True)},
        tags=["Dashboard"],
        operation_description="Returns joined user count "
        "per day for the current week (Monday to today)",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_current_week_joined_users()


class RFQOrderStatusCountAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: RFQOrderStatusCountSerializer()},
        tags=["Dashboard"],
        operation_description="Returns RFQ order count grouped by status",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_rfq_orders_count_by_status()


class MonthlyRevenueStatsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: MonthlyRevenueItemSerializer(many=True)},
        tags=["Dashboard"],
        operation_description="Returns total order revenue (GMV) "
        "for each month from January to the current month",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_monthly_revenue_stats()


class TopCompaniesByOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: TopCompanyByOrdersSerializer(many=True)},
        tags=["Dashboard"],
        operation_description="Returns top 5 companies by "
        "order count with total revenue",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_top_companies_by_orders()


class OrdersCountByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    @swagger_auto_schema(
        responses={200: OrdersCountByCategorySerializer(many=True)},
        tags=["Dashboard"],
        operation_description="Returns order counts for top 3 categories; "
        "all remaining categories are summed as 'Others'",
    )
    def get(self, request, *args, **kwargs):
        return AdminService(request=request).get_orders_count_by_category()
