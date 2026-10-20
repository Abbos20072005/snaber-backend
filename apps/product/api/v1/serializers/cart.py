from rest_framework import serializers

from apps.product.api.v1.serializers.products import ProductListSerializer
from apps.product.api.v1.utils.cart import get_cart_item_total_price
from apps.product.models import Cart, CartItem, Product


class CartCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
    )
    quantity = serializers.IntegerField()


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "quantity",
            "total_price",
        )

    def get_total_price(self, obj):
        return get_cart_item_total_price(obj)


class CartResponseSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    products = serializers.IntegerField()


class CartListSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, source="cartitem_set")

    class Meta:
        model = Cart
        fields = ("id", "items")
