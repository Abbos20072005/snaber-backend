from rest_framework import serializers

from apps.product.api.v1.serializers.categories import CategorySimpleSerializer
from apps.product.models import Attribute


class AttributeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "attribute_type",
            "category",
            "is_filterable",
        )


class AttributeSimpleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    attribute_type = serializers.CharField()


class AttributeValueFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    value_uz = serializers.CharField()
    value_ru = serializers.CharField()
    value_en = serializers.CharField()
    image = serializers.ImageField()


class AttributeListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    attribute_type = serializers.CharField()
    category = CategorySimpleSerializer()
    is_filterable = serializers.BooleanField()
    values = AttributeValueFilterSerializer(
        source="attribute_values",
        many=True,
        read_only=True,
    )


class AttributeFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    attribute_type = serializers.CharField()
    values = AttributeValueFilterSerializer(
        source="attribute_values",
        many=True,
        read_only=True,
    )
