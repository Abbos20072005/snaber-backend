from apps.order.api.v1.filters.order import OrderFilter
from apps.order.models import Order


class CompanyOrderRepository:
    def get(self, pk, query_params):
        qs = (
            Order.objects.filter(company_id=pk)
            .select_related("buyer", "company")
            .prefetch_related(
                "items__product_variant__product",
                "items__product_variant__product_variant_medias",
                "items__category",
                "items__attributes__attribute",
                "items__attributes__value_option",
            )
        )
        return OrderFilter(query_params, queryset=qs).qs
