from django.contrib import admin

from apps.order.models import Order, OrderItem, RFQOrderItemAttribute


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product_variant",
        "attribute_stock",
        "quantity",
        "price_min",
        "price_max",
    )
    autocomplete_fields = ["product_variant", "attribute_stock"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = (
        "id",
        "buyer",
        "company",
        "order_type",
        "status",
        "is_closed",
        "created_at",
        "accepted_by_buyer",
        "accepted_by_seller",
        "rejected_by_buyer",
        "rejected_by_seller",
    )
    list_filter = (
        "order_type",
        "status",
        "is_closed",
        "created_at",
        "accepted_by_buyer",
        "accepted_by_seller",
        "rejected_by_buyer",
        "rejected_by_seller",
    )
    search_fields = ("id", "buyer__username", "buyer__email", "company__name")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "General Information",
            {
                "fields": (
                    "buyer",
                    "company",
                    "order_type",
                    "status",
                    "discount",
                    "discount_budget",
                    "is_closed",
                    "created_at",
                    "updated_at",
                    "accepted_by_buyer",
                    "accepted_by_seller",
                    "rejected_by_buyer",
                    "rejected_by_seller",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": ("deadline",),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("buyer", "company")
            .prefetch_related("items__product_variant")
        )


class RFQOrderItemAttributeInline(admin.TabularInline):
    model = RFQOrderItemAttribute
    extra = 0
    fields = ("attribute", "value_option", "value")
    autocomplete_fields = ["attribute", "value_option"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    inlines = [RFQOrderItemAttributeInline]
    list_display = (
        "id",
        "order",
        "product_variant",
        "attribute_stock",
        "quantity",
        "price_min",
        "price_max",
    )
    list_filter = ("order",)
    search_fields = ("order__id", "product_variant__sku_variant")
