from rest_framework import serializers

from apps.company.api.v1.serializers.companies import CompanyListSerializer
from apps.company.models import Company
from apps.core.exceptions import ValidationError
from apps.order.models import Order, OrderItem
from apps.product.api.v1.utils.currency import convert_price, get_target_currency
from apps.product.models import (
    Attribute,
    AttributeValue,
    Category,
    Variant,
    VariantAttributeStock,
)


class VariantMediaSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    file = serializers.FileField()
    product_media_type = serializers.CharField()


class SimpleProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    product_type = serializers.CharField()
    price_type = serializers.CharField()
    price_min = serializers.DecimalField(max_digits=55, decimal_places=2)
    price_max = serializers.DecimalField(max_digits=55, decimal_places=2)
    moq = serializers.IntegerField()
    sku = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("price_min") is not None:
                data["price_min"] = convert_price(data["price_min"], target)
            if data.get("price_max") is not None:
                data["price_max"] = convert_price(data["price_max"], target)
        return data


class ProductVariantDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    sku_variant = serializers.CharField()
    price_override = serializers.DecimalField(max_digits=14, decimal_places=2)
    moq_override = serializers.IntegerField()
    stock_quantity = serializers.IntegerField()
    medias = VariantMediaSerializer(
        source="product_variant_medias", many=True, read_only=True
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("price_override") is not None:
            data["price_override"] = convert_price(data["price_override"], target)
        return data


class RFQAttributeValueSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    value = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)


class RFQAttributeFieldSerializer(serializers.Serializer):
    """Output serializer for displaying RFQ item attributes in order list."""

    id = serializers.IntegerField(read_only=True)
    attribute_id = serializers.IntegerField(source="attribute.id", read_only=True)
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)
    attribute_type = serializers.CharField(
        source="attribute.attribute_type", read_only=True
    )
    value_option = RFQAttributeValueSerializer(read_only=True)
    value = serializers.CharField(read_only=True)


class RFQAttributeCreateSerializer(serializers.Serializer):
    """Input serializer for creating RFQ attributes on an order item."""

    attribute = serializers.PrimaryKeyRelatedField(queryset=Attribute.objects.all())
    value_option = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(), required=False, allow_null=True
    )
    value = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, data):
        attribute = data.get("attribute")
        value_option = data.get("value_option")
        value = data.get("value", "")

        if value_option:
            if value_option.attribute != attribute:
                raise serializers.ValidationError(
                    {
                        "value_option": "Value does not belong "
                        "to the specified attribute."
                    }
                )
        elif not value:
            raise serializers.ValidationError(
                {"value": f"Attribute '{attribute.name}' requires a value."}
            )

        return data


class OrderAttributeStockValueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class OrderAttributeStockSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute_values = OrderAttributeStockValueSerializer(many=True)
    quantity = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(source="product_variant.product", read_only=True)
    variant = ProductVariantDetailSerializer(source="product_variant", read_only=True)
    attribute_stock = OrderAttributeStockSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    attributes = RFQAttributeFieldSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "variant",
            "attribute_stock",
            "quantity",
            "price_min",
            "price_max",
            "total_price",
            "category",
            "description",
            "attributes",
        )

    def get_total_price(self, obj):
        price = (
            obj.price_min
            or obj.price_max
            or obj.product_variant.price_override
            or obj.product_variant.product.price_min
            or 0
        )
        return obj.quantity * price

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("price_min") is not None:
                data["price_min"] = convert_price(data["price_min"], target)
            if data.get("price_max") is not None:
                data["price_max"] = convert_price(data["price_max"], target)
            if data.get("total_price") is not None:
                data["total_price"] = convert_price(data["total_price"], target)
        return data


class OrderItemCreateSerializer(serializers.Serializer):
    product_variant = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all())
    attribute_stock = serializers.PrimaryKeyRelatedField(
        queryset=VariantAttributeStock.objects.all(),
        required=False,
        allow_null=True,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    description = serializers.CharField(required=False, allow_null=True)
    quantity = serializers.IntegerField()
    price_min = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False, allow_null=True
    )
    price_max = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False, allow_null=True
    )
    attributes = RFQAttributeCreateSerializer(many=True, required=False)

    def validate(self, data):
        variant = data.get("product_variant")
        quantity = data.get("quantity")
        attribute_stock = data.get("attribute_stock")

        if attribute_stock and attribute_stock.variant != variant:
            raise ValidationError(
                message="Attribute stock does not belong to this variant",
                message_key="invalid_attribute_stock",
            )

        if variant and quantity:
            available = (
                attribute_stock.quantity if attribute_stock else variant.stock_quantity
            )
            moq = variant.moq_override or variant.product.moq
            if quantity < moq:
                raise ValidationError(
                    message=f"Minimum order quantity is {moq}",
                    message_key="quantity_below_moq",
                )
            elif quantity > available:
                raise ValidationError(
                    message=f"Available quantity is {available}",
                    message_key="quantity_exceeds_available",
                )

        return data


class OrderCreateUpdateSerializer(serializers.Serializer):
    order_type = serializers.ChoiceField(
        choices=Order.OrderType.choices, required=False
    )
    status = serializers.ChoiceField(choices=Order.OrderStatus.choices, required=False)
    is_closed = serializers.BooleanField(required=False)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    deadline = serializers.DateTimeField(required=False, allow_null=True)
    budget = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False, allow_null=True
    )
    discount = serializers.IntegerField(required=False)
    items = OrderItemCreateSerializer(many=True, required=False)

    def validate_order_type(self, value):
        if value == Order.OrderType.BOTH:
            raise serializers.ValidationError(
                "'Both' order type is auto-detected from items. "
                "Choose 'ready' or 'rfq', or omit it."
            )
        return value


class OrderItemUpdateQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

class BuyerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    country = serializers.CharField()
    role = serializers.CharField()
    image = serializers.ImageField()



class OrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    buyer =BuyerSerializer(read_only=True)
    company = CompanyListSerializer(read_only=True)
    order_type = serializers.CharField()
    status = serializers.CharField()
    is_closed = serializers.BooleanField(read_only=True)
    accepted_by_buyer = serializers.BooleanField(read_only=True)
    accepted_by_seller = serializers.BooleanField(read_only=True)
    rejected_by_buyer = serializers.BooleanField(read_only=True)
    rejected_by_seller = serializers.BooleanField(read_only=True)
    deadline = serializers.DateTimeField(read_only=True)
    budget = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    discount = serializers.IntegerField(read_only=True)
    discount_budget = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    total_price = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            price = (
                item.price_min
                or item.price_max
                or item.product_variant.price_override
                or item.product_variant.product.price_min
                or 0
            )
            total += item.quantity * price
        return total

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("budget") is not None:
                data["budget"] = convert_price(data["budget"], target)
            if data.get("total_price") is not None:
                data["total_price"] = convert_price(data["total_price"], target)
            if data.get("discount_budget") is not None:
                data["discount_budget"] = convert_price(data["discount_budget"], target)
        return data
