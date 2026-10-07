from rest_framework import serializers

from apps.product.api.v1.serializers.products import ProductListSerializer


class FavouriteListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = ProductListSerializer(read_only=True)


class FavouriteCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    is_favourite = serializers.BooleanField()
