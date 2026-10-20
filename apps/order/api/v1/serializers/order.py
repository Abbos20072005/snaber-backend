from rest_framework import serializers

from apps.core.exceptions import ValidationError
from apps.order.models import OrderItem
from apps.product.api.v1.serializers.products import UnitBaseSerialzer
from apps.product.models import Product


class SimpleProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    sku = serializers.CharField()
    image = serializers.SerializerMethodField()
    unit = UnitBaseSerialzer(allow_null=True)
    stock_quantity = serializers.IntegerField()

    def get_image(self, obj):
        first = obj.images.all()[0] if obj.images.all() else None
        if not first or not first.file:
            return None
        request = self.context.get("request")
        url = first.file.url
        return request.build_absolute_uri(url) if request else url


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "quantity",
            "price",
            "total_price",
        )

    def get_total_price(self, obj):
        return obj.quantity * obj.price


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product = data["product"]
        if data["quantity"] > product.stock_quantity:
            raise ValidationError(
                message=f"Available quantity is {product.stock_quantity}",
                message_key="quantity_exceeds_available",
            )
        return data


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True, required=False)


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
    buyer = BuyerSerializer(read_only=True)
    budget = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    total_price = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)

    def get_total_price(self, obj):
        return sum(item.quantity * item.price for item in obj.items.all())
