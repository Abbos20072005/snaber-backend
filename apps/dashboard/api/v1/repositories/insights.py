from datetime import timedelta
from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Max,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

from apps.authentication.models import User
from apps.order.models import Order, OrderItem
from apps.product.models import Cart, CartItem, Product

PERIOD_DAYS = {"7d": 7, "30d": 30, "90d": 90, "365d": 365}
DEFAULT_PERIOD = "30d"

LOW_STOCK_THRESHOLD = 5
DEAD_STOCK_DAYS = 90
ABANDONED_AFTER_HOURS = 24
LIST_LIMIT = 10

_MONEY = DecimalField(max_digits=20, decimal_places=2)
_LINE_TOTAL = ExpressionWrapper(F("price") * F("quantity"), output_field=_MONEY)


def _final_price(prefix=""):
    """Price after the discount, for a product or, with a prefix, a related product."""
    return ExpressionWrapper(
        F(f"{prefix}price")
        * (100 - F(f"{prefix}discount_percent"))
        / Value(Decimal(100)),
        output_field=_MONEY,
    )


class InsightsRepository:
    def resolve_period(self, period):
        days = PERIOD_DAYS.get(period) or PERIOD_DAYS[DEFAULT_PERIOD]
        end = timezone.localdate()
        start = end - timedelta(days=days - 1)
        previous_end = start - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days - 1)
        return {
            "days": days,
            "start": start,
            "end": end,
            "previous_start": previous_start,
            "previous_end": previous_end,
        }

    def _kpis(self, start, end):
        orders = Order.objects.filter(
            created_at__date__gte=start, created_at__date__lte=end
        )
        items = OrderItem.objects.filter(
            order__created_at__date__gte=start, order__created_at__date__lte=end
        )
        totals = items.aggregate(
            revenue=Coalesce(Sum(_LINE_TOTAL), Value(0), output_field=_MONEY),
            units_sold=Coalesce(Sum("quantity"), 0),
        )
        orders_count = orders.count()
        buyer_ids = list(orders.values_list("buyer_id", flat=True).distinct())
        # A buyer is "returning" when they ordered before this period too.
        returning = (
            Order.objects.filter(buyer_id__in=buyer_ids, created_at__date__lt=start)
            .values("buyer_id")
            .distinct()
            .count()
            if buyer_ids
            else 0
        )
        revenue = totals["revenue"]
        return {
            "revenue": revenue,
            "orders_count": orders_count,
            "average_order_value": (
                (revenue / orders_count).quantize(Decimal("0.01"))
                if orders_count
                else Decimal(0)
            ),
            "units_sold": totals["units_sold"],
            "new_users": User.objects.filter(
                created_at__date__gte=start, created_at__date__lte=end
            ).count(),
            "active_buyers": len(buyer_ids),
            "returning_buyers": returning,
        }

    def _daily(self, start, end):
        revenue_by_day = {
            row["day"]: row
            for row in OrderItem.objects.filter(
                order__created_at__date__gte=start, order__created_at__date__lte=end
            )
            .annotate(day=TruncDate("order__created_at"))
            .values("day")
            .annotate(revenue=Coalesce(Sum(_LINE_TOTAL), Value(0), output_field=_MONEY))
        }
        orders_by_day = {
            row["day"]: row["count"]
            for row in Order.objects.filter(
                created_at__date__gte=start, created_at__date__lte=end
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
        }
        series = []
        day = start
        while day <= end:
            series.append(
                {
                    "date": day,
                    "revenue": revenue_by_day.get(day, {}).get("revenue", Decimal(0)),
                    "orders_count": orders_by_day.get(day, 0),
                }
            )
            day += timedelta(days=1)
        return series

    def get_overview(self, period):
        window = self.resolve_period(period)
        return {
            "period": period if period in PERIOD_DAYS else DEFAULT_PERIOD,
            "days": window["days"],
            "start": window["start"],
            "end": window["end"],
            "previous_start": window["previous_start"],
            "previous_end": window["previous_end"],
            "current": self._kpis(window["start"], window["end"]),
            "previous": self._kpis(window["previous_start"], window["previous_end"]),
            "daily": self._daily(window["start"], window["end"]),
        }

    def get_abandoned_carts(self):
        cutoff = timezone.now() - timedelta(hours=ABANDONED_AFTER_HOURS)
        # Items leave the cart when an order is placed, so a cart that still has items
        # and was not touched for a day was abandoned.
        carts = (
            CartItem.objects.filter(quantity__gt=0)
            .values("cart_id")
            .annotate(
                last_activity=Max("updated_at"),
                items_count=Count("id"),
                total=Coalesce(
                    Sum(F("quantity") * _final_price("product__")),
                    Value(0),
                    output_field=_MONEY,
                ),
            )
            .filter(last_activity__lt=cutoff)
        )
        rows = list(carts.order_by("-total"))
        owners = {
            c["id"]: c
            for c in Cart.objects.filter(
                id__in=[r["cart_id"] for r in rows[:LIST_LIMIT]]
            ).values("id", "user__full_name", "user__phone_number", "session_key")
        }
        top = []
        for row in rows[:LIST_LIMIT]:
            owner = owners.get(row["cart_id"], {})
            top.append(
                {
                    "customer": owner.get("user__full_name")
                    or owner.get("user__phone_number")
                    or "",
                    "phone_number": owner.get("user__phone_number") or "",
                    "is_guest": not owner.get("user__phone_number")
                    and not owner.get("user__full_name"),
                    "items_count": row["items_count"],
                    "total": row["total"],
                    "last_activity": row["last_activity"],
                }
            )
        return {
            "after_hours": ABANDONED_AFTER_HOURS,
            "carts_count": len(rows),
            "total_value": sum((r["total"] for r in rows), Decimal(0)),
            "top": top,
        }

    def get_stock_alerts(self):
        active = Product.objects.filter(is_active=True)
        low = active.filter(
            stock_quantity__gt=0, stock_quantity__lte=LOW_STOCK_THRESHOLD
        )
        out = active.filter(stock_quantity=0)

        since = timezone.now() - timedelta(days=DEAD_STOCK_DAYS)
        sold_recently = OrderItem.objects.filter(order__created_at__gte=since).values(
            "product_id"
        )
        dead = (
            active.filter(stock_quantity__gt=0, created_at__lt=since)
            .exclude(id__in=sold_recently)
            .annotate(
                stock_value=ExpressionWrapper(
                    F("stock_quantity") * _final_price(), output_field=_MONEY
                )
            )
        )

        def rows(queryset, order, with_value=False):
            result = []
            for p in queryset.order_by(*order)[:LIST_LIMIT]:
                row = {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "stock_quantity": p.stock_quantity,
                }
                if with_value:
                    row["stock_value"] = p.stock_value
                result.append(row)
            return result

        return {
            "low_stock_threshold": LOW_STOCK_THRESHOLD,
            "dead_stock_days": DEAD_STOCK_DAYS,
            "low_stock_count": low.count(),
            "out_of_stock_count": out.count(),
            "dead_stock_count": dead.count(),
            "dead_stock_value": dead.aggregate(
                v=Coalesce(Sum("stock_value"), Value(0), output_field=_MONEY)
            )["v"],
            "low_stock": rows(low, ["stock_quantity", "name"]),
            "out_of_stock": rows(out, ["-updated_at"]),
            "dead_stock": rows(dead, ["-stock_value"], with_value=True),
        }
