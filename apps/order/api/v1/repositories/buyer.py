from apps.order.api.v1.filters.order import OrderFilter
from apps.order.api.v1.repositories.order import ORDER_PREFETCH
from apps.order.models import Order


class BuyerOrderRepository:
    def get(self, pk, query_params):
        qs = (
            Order.objects.filter(buyer=pk)
            .select_related("buyer")
            .prefetch_related(*ORDER_PREFETCH)
        )
        return OrderFilter(query_params, queryset=qs).qs
