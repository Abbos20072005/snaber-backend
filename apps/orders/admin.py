import re

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.catalog.admin import AuthorMixin
from apps.orders.models import ALLOWED_TRANSITIONS, Order, OrderItem, OrderStatus


def money(value):
    return f"{value:,}".replace(",", " ") + " so'm"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("sku_link", "name", "price_display", "pack", "qty", "amount_display")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Artikul")
    def sku_link(self, obj):
        # Mahsulot keyin o'chirilgan bo'lishi mumkin: artikul baribir saqlanib qoladi.
        if obj.product_id is None:
            return obj.sku
        url = reverse("admin:catalog_product_change", args=[obj.product_id])
        return format_html('<a href="{}">{}</a>', url, obj.sku)

    @admin.display(description="Qadoq narxi")
    def price_display(self, obj):
        return money(obj.price)

    @admin.display(description="Summa")
    def amount_display(self, obj):
        return money(obj.amount)


@admin.register(Order)
class OrderAdmin(AuthorMixin, admin.ModelAdmin):
    list_display = ("number_display", "name", "phone", "total_display", "status", "created_at")
    list_display_links = ("number_display",)
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = ("name", "phone")
    date_hierarchy = "created_at"
    list_per_page = 50
    inlines = (OrderItemInline,)
    readonly_fields = (
        "number_display",
        "name",
        "phone",
        "comment",
        "total_display",
        "ip_address",
        "created_at",
        "modified_at",
        "modified_by",
    )
    fields = readonly_fields[:5] + ("status",) + readonly_fields[5:]

    def has_add_permission(self, request):
        # Buyurtmalar faqat saytdagi savatdan keladi.
        return False

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        term = search_term.strip().lstrip("№#")
        if term.isdigit():
            queryset |= self.model.objects.filter(pk=int(term))
        # Telefon "+998901234567" ko'rinishida: "90 123 45" kabi yozilsa ham topilsin.
        digits = re.sub(r"\D", "", search_term)
        if len(digits) >= 4:
            queryset |= self.model.objects.filter(phone__contains=digits)
        return queryset, may_have_duplicates

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            order = self._editing_order(request)
            if order is not None:
                allowed = {order.status, *ALLOWED_TRANSITIONS[order.status]}
                kwargs["choices"] = [
                    choice for choice in OrderStatus.choices if choice[0] in allowed
                ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def _editing_order(self, request):
        match = request.resolver_match
        object_id = match.kwargs.get("object_id") if match else None
        return self.model.objects.filter(pk=object_id).first() if object_id else None

    @admin.display(description="Raqami", ordering="id")
    def number_display(self, obj):
        return f"№{obj.number}"

    @admin.display(description="Jami", ordering="total")
    def total_display(self, obj):
        return money(obj.total)
