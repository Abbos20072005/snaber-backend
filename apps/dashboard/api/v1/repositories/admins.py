from django.db.models import (
    Case,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, ExtractMonth, TruncDate
from django.utils import timezone

from apps.authentication.models import User
from apps.order.models import Order, OrderItem
from apps.product.models import Category, Product


class AdminRepository:
    def get_today_orders_count(self):
        today = timezone.now().date()
        return Order.objects.filter(created_at__date=today).count()

    def get_user_counts(self):
        counts = User.objects.aggregate(
            buyers=Count("id", filter=Q(role=User.Roles.BUYER)),
            admins=Count("id", filter=Q(role=User.Roles.ADMIN)),
        )
        return {**counts, "total_users": counts["buyers"] + counts["admins"]}

    def get_current_week_joined_users(self):
        today = timezone.now().date()
        week_start = today - timezone.timedelta(days=today.weekday())

        return list(
            User.objects.filter(
                created_at__date__gte=week_start,
                created_at__date__lte=today,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .annotate(
                day=Case(
                    When(date__week_day=2, then=Value("Monday")),
                    When(date__week_day=3, then=Value("Tuesday")),
                    When(date__week_day=4, then=Value("Wednesday")),
                    When(date__week_day=5, then=Value("Thursday")),
                    When(date__week_day=6, then=Value("Friday")),
                    When(date__week_day=7, then=Value("Saturday")),
                    When(date__week_day=1, then=Value("Sunday")),
                )
            )
            .order_by("date")
            .values("day", "count")
        )

    def get_orders_count_by_category(self):
        top = list(
            OrderItem.objects.filter(product__category__isnull=False)
            .values("product__category_id")
            .annotate(orders_count=Count("order", distinct=True))
            .order_by("-orders_count")[:3]
        )
        top_ids = [row["product__category_id"] for row in top]
        names = {
            category.id: category.name
            for category in Category.objects.filter(id__in=top_ids)
        }
        result = [
            {
                "category_name": names.get(row["product__category_id"], ""),
                "orders_count": row["orders_count"],
            }
            for row in top
        ]
        others = (
            OrderItem.objects.filter(product__category__isnull=False)
            .exclude(product__category_id__in=top_ids)
            .values("order_id")
            .distinct()
            .count()
        )
        if others:
            result.append({"category_name": "Others", "orders_count": others})
        return result

    def get_top_products_by_orders(self):
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        line_total = ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=decimal_field,
        )
        top = list(
            OrderItem.objects.values("product_id")
            .annotate(
                orders_count=Count("order", distinct=True),
                orders_total=Coalesce(
                    Sum(line_total), Value(0), output_field=decimal_field
                ),
            )
            .order_by("-orders_count")[:5]
        )
        names = {
            product.id: product.name
            for product in Product.objects.filter(id__in=[r["product_id"] for r in top])
        }
        return [
            {
                "product_name": names.get(row["product_id"], ""),
                "orders_count": row["orders_count"],
                "orders_total": row["orders_total"],
            }
            for row in top
        ]

    def get_monthly_revenue_stats(self):
        now = timezone.now()
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        line_total = ExpressionWrapper(
            F("items__price") * F("items__quantity"),
            output_field=decimal_field,
        )

        return list(
            Order.objects.filter(
                created_at__year=now.year,
                created_at__month__lte=now.month,
            )
            .annotate(month_num=ExtractMonth("created_at"))
            .values("month_num")
            .annotate(
                total=Coalesce(Sum(line_total), Value(0), output_field=decimal_field)
            )
            .annotate(
                month=Case(
                    When(month_num=1, then=Value("January")),
                    When(month_num=2, then=Value("February")),
                    When(month_num=3, then=Value("March")),
                    When(month_num=4, then=Value("April")),
                    When(month_num=5, then=Value("May")),
                    When(month_num=6, then=Value("June")),
                    When(month_num=7, then=Value("July")),
                    When(month_num=8, then=Value("August")),
                    When(month_num=9, then=Value("September")),
                    When(month_num=10, then=Value("October")),
                    When(month_num=11, then=Value("November")),
                    When(month_num=12, then=Value("December")),
                )
            )
            .order_by("month_num")
            .values("month", "total")
        )
