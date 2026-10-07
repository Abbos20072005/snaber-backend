from django.db.models import (
    Count,
    Sum,
    Q,
    F,
    Value,
    DecimalField,
    IntegerField,
    ExpressionWrapper,
    Max,
    Case,
    When,
    CharField,
)
from django.db.models.functions import Coalesce, TruncMonth
from django.utils import timezone

from apps.order.models import Order


class BuyerRepository:
    def get_orders(self, user):
        return Order.objects.filter(buyer=user)

    def get_active_statuses(self):
        return [
            Order.OrderStatus.NEGOTIATION,
        ]

    def get_amount_expression(self):
        return ExpressionWrapper(
            F("items__quantity")
            * Coalesce(
                F("items__product_variant__price_override"),
                F("items__product_variant__product__price_max"),
                Value(0),
            ),
            output_field=DecimalField(max_digits=20, decimal_places=2),
        )

    def get_kpis(self, user):
        return self.get_orders(user).aggregate(
            total_orders=Coalesce(
                Count("id", distinct=True), Value(0), output_field=IntegerField()
            ),
            active_orders=Coalesce(
                Count(
                    "id", filter=Q(status__in=self.get_active_statuses()), distinct=True
                ),
                Value(0),
                output_field=IntegerField(),
            ),
            rfq_orders=Coalesce(
                Count("id", filter=Q(order_type=Order.OrderType.RFQ), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
            estimated_spend=Coalesce(
                Sum(self.get_amount_expression()),
                Value(0),
                output_field=DecimalField(max_digits=20, decimal_places=2),
            ),
        )

    def get_purchase_momentum(self, user):
        six_months_ago = timezone.now().date().replace(day=1) - timezone.timedelta(
            days=180
        )

        return (
            self.get_orders(user)
            .filter(created_at__date__gte=six_months_ago)
            .annotate(month_date=TruncMonth("created_at"))
            .values("month_date")
            .annotate(
                month=Case(
                    When(month_date__month=1, then=Value("jan")),
                    When(month_date__month=2, then=Value("feb")),
                    When(month_date__month=3, then=Value("mar")),
                    When(month_date__month=4, then=Value("apr")),
                    When(month_date__month=5, then=Value("may")),
                    When(month_date__month=6, then=Value("jun")),
                    When(month_date__month=7, then=Value("jul")),
                    When(month_date__month=8, then=Value("aug")),
                    When(month_date__month=9, then=Value("sep")),
                    When(month_date__month=10, then=Value("oct")),
                    When(month_date__month=11, then=Value("nov")),
                    When(month_date__month=12, then=Value("dec")),
                    output_field=CharField(),
                ),
                orders=Coalesce(
                    Count("id", distinct=True),
                    Value(0),
                    output_field=IntegerField(),
                ),
                spend=Coalesce(
                    Sum(self.get_amount_expression()),
                    Value(0),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                ),
            )
            .values("month", "orders", "spend")
            .order_by("month_date")
        )

    def get_status_mix(self, user):
        return self.get_orders(user).aggregate(
            negotiation=Coalesce(
                Count(
                    "id", filter=Q(status=Order.OrderStatus.NEGOTIATION), distinct=True
                ),
                Value(0),
                output_field=IntegerField(),
            ),
            accepted=Coalesce(
                Count("id", filter=Q(status=Order.OrderStatus.ACCEPTED), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
            rejected=Coalesce(
                Count("id", filter=Q(status=Order.OrderStatus.REJECTED), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
        )

    def get_order_type_split(self, user):
        return self.get_orders(user).aggregate(
            ready=Coalesce(
                Count("id", filter=Q(order_type=Order.OrderType.READY), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
            rfq=Coalesce(
                Count("id", filter=Q(order_type=Order.OrderType.RFQ), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
        )

    def get_recent_buying_activity(self, user):
        return (
            self.get_orders(user)
            .prefetch_related("items__product_variant__product")
            .annotate(
                product_name=Max("items__product_variant__product__name"),
                product_type=Max("items__product_variant__product__product_type"),
                quantity=Coalesce(
                    Sum("items__quantity"),
                    Value(0),
                    output_field=IntegerField(),
                ),
                amount=Coalesce(
                    Sum(self.get_amount_expression()),
                    Value(0),
                    output_field=DecimalField(max_digits=20, decimal_places=2),
                ),
            )
            .order_by("-created_at")[:5]
        )

    def get_summary(self, user):
        return self.get_orders(user).aggregate(
            total_orders=Coalesce(
                Count("id", distinct=True), Value(0), output_field=IntegerField()
            ),
            accepted_orders=Coalesce(
                Count("id", filter=Q(status=Order.OrderStatus.ACCEPTED), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
            orders_in_progress=Coalesce(
                Count(
                    "id", filter=Q(status__in=self.get_active_statuses()), distinct=True
                ),
                Value(0),
                output_field=IntegerField(),
            ),
            custom_requests=Coalesce(
                Count("id", filter=Q(order_type=Order.OrderType.RFQ), distinct=True),
                Value(0),
                output_field=IntegerField(),
            ),
        )
