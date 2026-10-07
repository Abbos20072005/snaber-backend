from django.db.models import (
    Case,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, ExtractMonth, TruncDate
from django.utils import timezone
from django.utils.translation import get_language

# Chat center metrics are disabled for the frontend
# from apps.chat.models import Conversation, Message
from apps.company.models import CompanyMember
from apps.order.models import Order
from apps.product.models import Product, Variant


class SellerRepository:
    category_name_fields = {
        "en": "items__product_variant__product__category__name_en",
        "ru": "items__product_variant__product__category__name_ru",
        "uz": "items__product_variant__product__category__name_uz",
    }

    category_other_names = {
        "en": "Others",
        "ru": "Другие",
        "uz": "Boshqalar",
    }

    def get_active_language_code(self):
        language_code = (get_language() or "en").split("-")[0]
        return language_code if language_code in self.category_name_fields else "en"

    def get_company_ids(self, user):
        return CompanyMember.objects.filter(user=user).values_list(
            "company_id", flat=True
        )

    def get_orders(self, user):
        return Order.objects.filter(
            items__product_variant__product__owner_id__in=self.get_company_ids(user)
        ).distinct()

    def get_revenue_orders(self, user):
        return self.get_orders(user).filter(
            status__in=[
                Order.OrderStatus.ACCEPTED,
            ]
        )

    def get_line_total_expression(self):
        decimal_field = DecimalField(max_digits=20, decimal_places=2)

        return ExpressionWrapper(
            Coalesce(
                F("items__price_min"),
                F("items__product_variant__price_override"),
                F("items__product_variant__product__price_min"),
                Value(0, output_field=decimal_field),
                output_field=decimal_field,
            )
            * F("items__quantity"),
            output_field=decimal_field,
        )

    def get_total_revenue(self, user, queryset=None):
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        orders = queryset if queryset is not None else self.get_revenue_orders(user)

        result = orders.aggregate(
            total=Coalesce(
                Sum(self.get_line_total_expression()),
                Value(0, output_field=decimal_field),
                output_field=decimal_field,
            )
        )

        return result["total"] or 0

    def get_monthly_growth(self, user):
        today = timezone.now().date()
        current_month_start = today.replace(day=1)
        previous_month_end = current_month_start - timezone.timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)

        current_revenue = self.get_total_revenue(
            user=user,
            queryset=self.get_revenue_orders(user).filter(
                created_at__date__gte=current_month_start
            ),
        )

        previous_revenue = self.get_total_revenue(
            user=user,
            queryset=self.get_revenue_orders(user).filter(
                created_at__date__gte=previous_month_start,
                created_at__date__lt=current_month_start,
            ),
        )

        if not previous_revenue:
            return 0

        return round(((current_revenue - previous_revenue) / previous_revenue) * 100, 2)

    # Chat center (unread chats metric) is disabled for the frontend
    # def get_unread_buyer_chats_count(self, user):
    #     return (
    #         Message.objects.filter(
    #             conversation__seller=user,
    #             conversation__buyer__isnull=False,
    #             is_read=False,
    #         )
    #         .exclude(sender=user)
    #         .count()
    #     )

    def get_dispatch_due_today_count(self, user):
        today = timezone.now().date()

        return self.get_revenue_orders(user).filter(deadline__date=today).count()

    def get_confirmed_orders_count(self, user):
        return self.get_revenue_orders(user).count()

    def get_buyers_count(self, user):
        return (
            self.get_orders(user)
            .values_list(
                "buyer_id",
                flat=True,
            )
            .distinct()
            .count()
        )

    def get_rfq_stats(self, user):
        rfq_orders = self.get_orders(user).filter(order_type=Order.OrderType.RFQ)

        total_rfqs = rfq_orders.count()

        won_rfqs = rfq_orders.filter(
            status__in=[
                Order.OrderStatus.ACCEPTED,
            ]
        ).count()

        rfq_win_rate = 0
        if total_rfqs:
            rfq_win_rate = round((won_rfqs / total_rfqs) * 100, 2)

        return {
            "total_rfqs": total_rfqs,
            "won_rfqs": won_rfqs,
            "rfq_win_rate": rfq_win_rate,
        }

    def get_revenue_momentum(self, user):
        now = timezone.now()
        decimal_field = DecimalField(max_digits=20, decimal_places=2)

        return list(
            self.get_revenue_orders(user)
            .filter(
                created_at__year=now.year,
                created_at__month__lte=now.month,
            )
            .annotate(month_num=ExtractMonth("created_at"))
            .values("month_num")
            .annotate(
                revenue=Coalesce(
                    Sum(self.get_line_total_expression()),
                    Value(0, output_field=decimal_field),
                    output_field=decimal_field,
                ),
                orders=Count("id", distinct=True),
                quotes=Count(
                    "id",
                    filter=Q(order_type=Order.OrderType.RFQ),
                    distinct=True,
                ),
            )
            .annotate(
                month=Case(
                    When(month_num=1, then=Value("Jan")),
                    When(month_num=2, then=Value("Feb")),
                    When(month_num=3, then=Value("Mar")),
                    When(month_num=4, then=Value("Apr")),
                    When(month_num=5, then=Value("May")),
                    When(month_num=6, then=Value("Jun")),
                    When(month_num=7, then=Value("Jul")),
                    When(month_num=8, then=Value("Aug")),
                    When(month_num=9, then=Value("Sep")),
                    When(month_num=10, then=Value("Oct")),
                    When(month_num=11, then=Value("Nov")),
                    When(month_num=12, then=Value("Dec")),
                )
            )
            .order_by("month_num")
            .values(
                "month",
                "revenue",
                "orders",
                "quotes",
            )
        )

    def get_sales_by_category(self, user):
        seller_company_ids = self.get_company_ids(user)
        language_code = self.get_active_language_code()
        active_category_name_field = self.category_name_fields[language_code]
        other_category_name = self.category_other_names[language_code]

        top_categories = (
            Order.objects.filter(
                items__product_variant__product__category__isnull=False,
                items__product_variant__product__owner_id__in=seller_company_ids,
            )
            .values("items__product_variant__product__category_id")
            .annotate(orders_count=Count("id", distinct=True))
            .order_by("-orders_count")
            .values_list(
                "items__product_variant__product__category_id",
                flat=True,
            )[:3]
        )

        return list(
            Order.objects.filter(
                items__product_variant__product__category__isnull=False,
                items__product_variant__product__owner_id__in=seller_company_ids,
            )
            .annotate(
                category_name=Case(
                    When(
                        items__product_variant__product__category_id__in=top_categories,
                        then=F(active_category_name_field),
                    ),
                    default=Value(other_category_name),
                ),
                category_name_uz=Case(
                    When(
                        items__product_variant__product__category_id__in=top_categories,
                        then=F("items__product_variant__product__category__name_uz"),
                    ),
                    default=Value(self.category_other_names["uz"]),
                ),
                category_name_ru=Case(
                    When(
                        items__product_variant__product__category_id__in=top_categories,
                        then=F("items__product_variant__product__category__name_ru"),
                    ),
                    default=Value(self.category_other_names["ru"]),
                ),
                category_name_en=Case(
                    When(
                        items__product_variant__product__category_id__in=top_categories,
                        then=F("items__product_variant__product__category__name_en"),
                    ),
                    default=Value(self.category_other_names["en"]),
                ),
            )
            .values(
                "category_name",
                "category_name_uz",
                "category_name_ru",
                "category_name_en",
            )
            .annotate(
                orders_count=Count("id", distinct=True),
            )
            .order_by(
                Case(
                    When(category_name=other_category_name, then=Value(1)),
                    default=Value(0),
                ),
                "-orders_count",
            )
        )

    # Chat center (buyer engagement metric) is disabled for the frontend
    # def get_buyer_engagement(self, user):
    #     today = timezone.now().date()
    #     week_start = today - timezone.timedelta(days=today.weekday())
    #
    #     return list(
    #         Conversation.objects.filter(
    #             created_at__date__gte=week_start,
    #             created_at__date__lte=today,
    #             seller=user,
    #         )
    #         .annotate(
    #             views=Value(0, output_field=IntegerField()),
    #             day=Case(
    #                 When(created_at__week_day=2, then=Value("Monday")),
    #                 When(created_at__week_day=3, then=Value("Tuesday")),
    #                 When(created_at__week_day=4, then=Value("Wednesday")),
    #                 When(created_at__week_day=5, then=Value("Thursday")),
    #                 When(created_at__week_day=6, then=Value("Friday")),
    #                 When(created_at__week_day=7, then=Value("Saturday")),
    #                 When(created_at__week_day=1, then=Value("Sunday")),
    #             ),
    #         )
    #         .values("day", "views")
    #         .annotate(chats=Count("id"))
    #         .order_by("day")
    #     )

    def get_rfq_pipeline(self, user):
        return (
            self.get_orders(user)
            .filter(order_type=Order.OrderType.RFQ)
            .aggregate(
                negotiation=Count(
                    "id",
                    filter=Q(status=Order.OrderStatus.NEGOTIATION),
                ),
                accepted=Count(
                    "id",
                    filter=Q(status=Order.OrderStatus.ACCEPTED),
                ),
                rejected=Count(
                    "id",
                    filter=Q(status=Order.OrderStatus.REJECTED),
                ),
            )
        )

    def get_products_with_order_stats(self, user):
        decimal_field = DecimalField(max_digits=20, decimal_places=2)
        integer_field = IntegerField()

        line_total = ExpressionWrapper(
            Coalesce(
                F("product_variants__order_items__price_min"),
                F("product_variants__price_override"),
                F("price_min"),
                Value(0, output_field=decimal_field),
                output_field=decimal_field,
            )
            * F("product_variants__order_items__quantity"),
            output_field=decimal_field,
        )

        return Product.objects.filter(owner_id__in=self.get_company_ids(user)).annotate(
            orders_count=Coalesce(
                Count(
                    "product_variants__order_items__order",
                    filter=Q(product_variants__order_items__order__isnull=False),
                    distinct=True,
                ),
                Value(0),
                output_field=integer_field,
            ),
            revenue=Coalesce(
                Sum(
                    line_total,
                    filter=Q(
                        product_variants__order_items__order__status__in=[
                            Order.OrderStatus.ACCEPTED,
                        ]
                    ),
                ),
                Value(0, output_field=decimal_field),
                output_field=decimal_field,
            ),
            stock=Coalesce(
                Sum("product_variants__stock_quantity"),
                Value(0, output_field=integer_field),
                output_field=integer_field,
            ),
        )

    def get_top_products(self, user):
        return sorted(
            self.get_products_with_order_stats(user),
            key=lambda product: (
                -(product.orders_count or 0),
                -(product.revenue or 0),
                product.name or "",
            ),
        )[:5]

    def get_order_total(self, order):
        price = order.product_variant.price_override

        if price is None:
            price = order.product_variant.product.price_min

        return (price or 0) * order.quantity

    def get_recent_orders(self, user):
        return (
            self.get_orders(user)
            .select_related(
                "buyer",
                "company",
                "conversation",
            )
            .order_by("-created_at")[:5]
        )
