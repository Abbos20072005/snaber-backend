from django.contrib import admin

from apps.order.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price")
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = (
        "id",
        "buyer",
        "budget",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("id", "buyer__username", "buyer__email", "buyer__phone_number")

    fields = ("buyer", "budget", "created_at", "updated_at")
    readonly_fields = ("budget", "created_at", "updated_at")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("buyer")
            .prefetch_related("items__product")
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price")
    list_filter = ("order",)
    search_fields = ("order__id", "product__name", "product__sku")
    autocomplete_fields = ["product"]
