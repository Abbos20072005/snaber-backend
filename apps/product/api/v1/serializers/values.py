from rest_framework import serializers

from apps.product.api.v1.serializers.attributes import AttributeSimpleSerializer
from apps.product.models import AttributeValue


class AttributeValueListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    value_uz = serializers.CharField()
    value_ru = serializers.CharField()
    value_en = serializers.CharField()
    image = serializers.FileField()
    attribute = AttributeSimpleSerializer()


class AttributeValueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ("id", "attribute", "value_uz", "value_ru", "value_en", "image")
