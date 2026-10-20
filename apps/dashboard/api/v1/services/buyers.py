from apps.core.services import BaseService
from apps.dashboard.api.v1.repositories.buyers import BuyerRepository
from apps.dashboard.api.v1.serializers.buyers import (
    BuyerKpiSerializer,
    BuyerPurchaseMomentumSerializer,
    BuyerRecentActivitySerializer,
)


class BuyerService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = BuyerRepository()

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

    def get_recent_buying_activity(self, *args, **kwargs):
        queryset = self.db.get_recent_buying_activity(self.request.user)
        return self.get_response(
            queryset,
            BuyerRecentActivitySerializer,
            many=True,
            context={"request": self.request},
        )
