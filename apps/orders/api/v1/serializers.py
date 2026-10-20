import re

from rest_framework import serializers

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from apps.orders.services import create_order

MAX_ITEMS = 100
MAX_QTY = 10_000
UZ_COUNTRY_CODE = "998"


def normalize_phone(value):
    """`90 123-45-67`, `+998 90 123 45 67` → `+998901234567`."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 9:
        digits = UZ_COUNTRY_CODE + digits
    if len(digits) != 12 or not digits.startswith(UZ_COUNTRY_CODE):
        raise serializers.ValidationError("Telefon raqamini +998 90 123-45-67 ko'rinishida yozing")
    return f"+{digits}"


class OrderItemCreateSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    qty = serializers.IntegerField(min_value=1, max_value=MAX_QTY)


class OrderCreateSerializer(serializers.ModelSerializer):
    """`{"name", "phone", "comment"?, "items": [{"sku", "qty"}]}`; `qty` — qadoqlar soni."""

    items = OrderItemCreateSerializer(many=True, allow_empty=False, max_length=MAX_ITEMS)

    class Meta:
        model = Order
        fields = ("name", "phone", "comment", "items")
        extra_kwargs = {"comment": {"required": False, "allow_blank": True, "max_length": 1000}}

    def validate_name(self, value):
        value = " ".join(value.split())
        if len(value) < 2:
            raise serializers.ValidationError("Ismingizni yozing")
        return value

    def validate_phone(self, value):
        return normalize_phone(value)

    def validate_items(self, items):
        skus = {item["sku"].strip() for item in items}
        products = Product.objects.filter(sku__in=skus, is_active=True).in_bulk(field_name="sku")

        errors = [
            {}
            if item["sku"].strip() in products
            else {"sku": ["Mahsulot topilmadi yoki sotuvda yo'q"]}
            for item in items
        ]
        if any(errors):
            raise serializers.ValidationError(errors)

        # Bir mahsulot ikki qatorda kelsa, bitta qatorga qo'shiladi.
        quantities = {}
        for item in items:
            sku = item["sku"].strip()
            quantities[sku] = quantities.get(sku, 0) + item["qty"]
        too_many = [sku for sku, qty in quantities.items() if qty > MAX_QTY]
        if too_many:
            raise serializers.ValidationError(
                f"Bitta mahsulotdan {MAX_QTY} qadoqdan ko'p bo'lmasin: {', '.join(too_many)}"
            )
        return [(products[sku], qty) for sku, qty in quantities.items()]

    def create(self, validated_data):
        return create_order(
            name=validated_data["name"],
            phone=validated_data["phone"],
            comment=validated_data.get("comment", ""),
            lines=validated_data["items"],
            ip_address=self.context.get("ip_address"),
        )


class OrderItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("sku", "name", "price", "pack", "qty", "amount")


class OrderRetrieveSerializer(serializers.ModelSerializer):
    """Created order with the prices it was actually priced at."""

    number = serializers.IntegerField(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("number", "status", "total", "created_at", "items")
