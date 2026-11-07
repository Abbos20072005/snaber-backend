from rest_framework import serializers

from apps.core.exceptions import ValidationError
from apps.product.api.v1.serializers.products import ProductListSerializer


class QuickOrderSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)

    def validate(self, data):
        if not data.get("text") and not data.get("file"):
            raise ValidationError(
                message="Send a list as text or as a file",
                message_key="list_required",
            )
        return data


class QuickOrderLineSerializer(serializers.Serializer):
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    matches = ProductListSerializer(many=True)
