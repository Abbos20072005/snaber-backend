from apps.core.services import BaseService
from apps.dashboard.api.v1.repositories.sellers import SellerRepository
from apps.dashboard.api.v1.serializers.sellers import (
    # BuyerEngagementSerializer,
    HeroSummarySerializer,
    KpiSerializer,
    RecentOrderSerializer,
    RevenueMomentumSerializer,
    RfqPipelineSerializer,
    SalesByCategorySerializer,
    TopProductSerializer,
)


class SellerService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = SellerRepository()

    def get_hero_summary(self, *args, **kwargs):
        user = self.request.user
        data = {
            "monthly_growth": self.db.get_monthly_growth(user),
            # Chat center (unread chats metric) is disabled for the frontend
            # "unread_buyer_chats": self.db.get_unread_buyer_chats_count(user),
            "dispatch_due_today": self.db.get_dispatch_due_today_count(user),
        }

        return self.get_response_object(
            data, HeroSummarySerializer, context={"request": self.request}
        )

    def get_kpis(self, *args, **kwargs):
        user = self.request.user

        total_revenue = self.db.get_total_revenue(user)
        confirmed_orders = self.db.get_confirmed_orders_count(user)
        buyers_count = self.db.get_buyers_count(user)
        rfq_stats = self.db.get_rfq_stats(user)
        monthly_growth = self.db.get_monthly_growth(user)

        data = [
            {
                "value": total_revenue,
                "delta": monthly_growth,
            },
            {
                "value": confirmed_orders,
                "delta": 0,
                "note": buyers_count,
            },
            {
                "value": rfq_stats["rfq_win_rate"],
                "delta": 0,
                "note": rfq_stats["total_rfqs"],
            },
        ]

        return self.get_response(
            data, KpiSerializer, many=True, context={"request": self.request}
        )

    def get_revenue_momentum(self, *args, **kwargs):
        data = self.db.get_revenue_momentum(self.request.user)
        return self.get_response(
            data,
            RevenueMomentumSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_sales_by_category(self, *args, **kwargs):
        data = self.db.get_sales_by_category(self.request.user)
        return self.get_response(
            data,
            SalesByCategorySerializer,
            many=True,
            context={"request": self.request},
        )

    # Chat center (buyer engagement metric) is disabled for the frontend
    # def get_buyer_engagement(self, *args, **kwargs):
    #     data = self.db.get_buyer_engagement(self.request.user)
    #     return self.get_response(
    #         data,
    #         BuyerEngagementSerializer,
    #         many=True,
    #         context={"request": self.request},
    #     )

    def get_rfq_pipeline(self, *args, **kwargs):
        data = self.db.get_rfq_pipeline(self.request.user)
        serializer = RfqPipelineSerializer(data)
        return self.get_response_object(
            serializer.data, RfqPipelineSerializer, context={"request": self.request}
        )

    def get_top_products(self, *args, **kwargs):
        data = self.db.get_top_products(self.request.user)
        return self.get_response(
            data, TopProductSerializer, many=True, context={"request": self.request}
        )

    def get_recent_orders(self, *args, **kwargs):
        data = self.db.get_recent_orders(self.request.user)
        return self.get_response(
            data, RecentOrderSerializer, many=True, context={"request": self.request}
        )

