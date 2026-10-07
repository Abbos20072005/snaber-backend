from apps.core.services import BaseService
from apps.dashboard.api.v1.repositories.buyers import BuyerRepository
from apps.dashboard.api.v1.serializers.buyers import (
    BuyerKpiSerializer,
    BuyerPurchaseMomentumSerializer,
    BuyerStatusMixSerializer,
    BuyerOrderTypeSplitSerializer,
    BuyerRecentActivitySerializer,
    BuyerSummarySerializer,
)


class BuyerService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = BuyerRepository()

    def get_acceptance_rate(self, total_orders, accepted_orders):
        if not total_orders:
            return 0

        return round((accepted_orders / total_orders) * 100, 2)

    def get_kpis(self, *args, **kwargs):
        data = self.db.get_kpis(self.request.user)
        return self.get_response_object(
            data, BuyerKpiSerializer, context={"request": self.request}
        )

    def get_purchase_momentum(self, *args, **kwargs):
        queryset = self.db.get_purchase_momentum(self.request.user)
        return self.get_response(
            queryset,
            BuyerPurchaseMomentumSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_status_mix(self, *args, **kwargs):
        stats = self.db.get_status_mix(self.request.user)

        data = [
            {
                "status": "negotiation",
                "count": stats["negotiation"],
            },
            {
                "status": "accepted",
                "count": stats["accepted"],
            },
            {
                "status": "rejected",
                "count": stats["rejected"],
            },
        ]

        return self.get_response(
            data, BuyerStatusMixSerializer, many=True, context={"request": self.request}
        )

    def get_order_type_split(self, *args, **kwargs):
        stats = self.db.get_order_type_split(self.request.user)

        data = [
            {
                "type": "ready",
                "count": stats["ready"],
            },
            {
                "type": "rfq",
                "count": stats["rfq"],
            },
        ]

        return self.get_response(
            data,
            BuyerOrderTypeSplitSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_recent_buying_activity(self, *args, **kwargs):
        queryset = self.db.get_recent_buying_activity(self.request.user)
        return self.get_response(
            queryset,
            BuyerRecentActivitySerializer,
            many=True,
            context={"request": self.request},
        )

    def get_summary(self, *args, **kwargs):
        stats = self.db.get_summary(self.request.user)

        data = {
            "acceptance_rate": self.get_acceptance_rate(
                total_orders=stats["total_orders"],
                accepted_orders=stats["accepted_orders"],
            ),
            "orders_in_progress": stats["orders_in_progress"],
            "custom_requests": stats["custom_requests"],
        }

        return self.get_response_object(
            data, BuyerSummarySerializer, context={"request": self.request}
        )
