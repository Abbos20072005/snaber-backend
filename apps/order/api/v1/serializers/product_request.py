import os

from rest_framework import serializers

from apps.authentication.api.v1.serializers.otp import PhoneField
from apps.core.exceptions import ValidationError
from apps.order.api.v1.serializers.order import BuyerSerializer
from apps.order.models import ProductRequest

ALLOWED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".pdf", ".xlsx", ".csv")
MAX_FILE_SIZE = 10 * 1024 * 1024


class ProductRequestItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    quantity = serializers.IntegerField(min_value=1, default=1)


class ProductRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    buyer = BuyerSerializer()
    comment = serializers.CharField()
    file = serializers.FileField()
    status = serializers.ChoiceField(choices=ProductRequest.Status.choices)
    answer = serializers.CharField()
    items = ProductRequestItemSerializer(many=True)
    created_at = serializers.DateTimeField()


class WantedProductSerializer(serializers.Serializer):
    name = serializers.CharField(source="product_name")
    requests_count = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    last_requested_at = serializers.DateTimeField()


class ProductRequestCreateSerializer(serializers.Serializer):
    # Needed when the buyer is not logged in, the account is created from it.
    phone_number = PhoneField(required=False)
    comment = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=False)
    # Sent as a JSON string next to the file in a multipart request.
    items = serializers.JSONField(required=False)

    def validate_file(self, file):
        if os.path.splitext(file.name)[1].lower() not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                message="Unsupported file type", message_key="unsupported_file"
            )
        if file.size > MAX_FILE_SIZE:
            raise ValidationError(
                message="File is too large", message_key="file_too_large"
            )
        return file

    def validate_items(self, value):
        serializer = ProductRequestItemSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def validate(self, data):
        if not (data.get("items") or data.get("file") or data.get("comment")):
            raise ValidationError(
                message="Add products, a file or a comment",
                message_key="request_empty",
            )
        return data


class ProductRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRequest
        fields = ("status", "answer")
