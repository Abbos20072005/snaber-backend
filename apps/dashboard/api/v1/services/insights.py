from apps.core.services import BaseService
from apps.dashboard.api.v1.repositories.insights import InsightsRepository
from apps.dashboard.api.v1.serializers.insights import (
    AbandonedCartsSerializer,
    OverviewSerializer,
    StockAlertsSerializer,
)


class InsightsService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = InsightsRepository()

    def get_overview(self, period):
        return self.get_response_object(
            self.db.get_overview(period),
            OverviewSerializer,
            context={"request": self.request},
        )

    def get_abandoned_carts(self):
        return self.get_response_object(
            self.db.get_abandoned_carts(),
            AbandonedCartsSerializer,
            context={"request": self.request},
        )

    def get_stock_alerts(self):
        return self.get_response_object(
            self.db.get_stock_alerts(),
            StockAlertsSerializer,
            context={"request": self.request},
        )
