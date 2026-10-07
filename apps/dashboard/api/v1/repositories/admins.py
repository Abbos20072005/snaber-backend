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
from apps.order.models import Order


class AdminRepository:
    def get_today_orders_count(self):
        today = timezone.now().date()
        return Order.objects.filter(
            created_at__date=today,
            order_type=Order.OrderType.READY,
        ).count()

    def get_today_rfq_orders_count(self):
        today = timezone.now().date()
        return Order.objects.filter(
            created_at__date=today,
            order_type=Order.OrderType.RFQ,
        ).count()

    def get_last_30_days_stats(self):
        since = timezone.now().date() - timezone.timedelta(days=30)
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        line_total = ExpressionWrapper(
            Coalesce(F("items__product_variant__price_override"), Value(0))
            * F("items__quantity"),
            output_field=decimal_field,
        )

        order_stats = Order.objects.filter(created_at__date__gte=since).aggregate(
            total_spent=Coalesce(Sum(line_total), Value(0), output_field=decimal_field),
            orders_count=Count("id", distinct=True),
        )

        user_stats = User.objects.filter(created_at__date__gte=since).aggregate(
            verified_sellers_count=Count(
                "id", filter=Q(role=User.Roles.SELLER, is_verified=True)
            ),
            total_users_count=Count("id"),
        )

        return {**order_stats, **user_stats}

    def get_user_counts(self):
        return User.objects.aggregate(
            sellers=Count("id", filter=Q(role=User.Roles.SELLER)),
            buyers=Count("id", filter=Q(role=User.Roles.BUYER)),
            moderators=Count("id", filter=Q(role=User.Roles.MODERATOR)),
            admins=Count("id", filter=Q(role=User.Roles.ADMIN)),
        )

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

    def get_rfq_orders_count_by_status(self):
        return Order.objects.filter(order_type=Order.OrderType.RFQ).aggregate(
            **{
                status: Count("id", filter=Q(status=status))
                for status, _ in Order.OrderStatus.choices
            }
        )

    def get_orders_count_by_category(self):
        top_names = (
            Order.objects.filter(items__category__isnull=False)
            .values("items__category__name")
            .annotate(counts=Count("id", distinct=True))
            .order_by("-counts")
            .values("items__category__name")[:3]
        )

        return list(
            Order.objects.filter(items__category__isnull=False)
            .annotate(
                category_name=Case(
                    When(
                        items__category__name__in=top_names,
                        then=F("items__category__name"),
                    ),
                    default=Value("Others"),
                )
            )
            .values("category_name")
            .annotate(orders_count=Count("id", distinct=True))
            .order_by(
                Case(
                    When(category_name="Others", then=Value(1)),
                    default=Value(0),
                ),
                "-orders_count",
            )
        )

    def get_top_companies_by_orders(self):
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        line_total = ExpressionWrapper(
            Coalesce(F("items__product_variant__price_override"), Value(0))
            * F("items__quantity"),
            output_field=decimal_field,
        )
        return list(
            Order.objects.values(
                company_name=F("company__name"),
            )
            .annotate(
                orders_count=Count("id"),
                orders_total=Coalesce(
                    Sum(line_total), Value(0), output_field=decimal_field
                ),
            )
            .order_by("-orders_count")[:5]
        )

    def get_monthly_revenue_stats(self):
        now = timezone.now()
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        line_total = ExpressionWrapper(
            Coalesce(F("items__product_variant__price_override"), Value(0))
            * F("items__quantity"),
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
