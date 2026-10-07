from rest_framework import serializers

from apps.product.models import Variant


class CommentImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    image = serializers.FileField()


class VariantShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku_variant = serializers.CharField(read_only=True)
    image = serializers.FileField(source="product.image", read_only=True)
    average_rating = serializers.DecimalField(
        max_digits=3, decimal_places=1, read_only=True
    )


class CommentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    image = serializers.FileField(read_only=True)


class CommentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    variant = VariantShortSerializer(read_only=True)
    user = CommentUserSerializer(read_only=True)
    text = serializers.CharField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    images = CommentImageSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class CommentCreateSerializer(serializers.Serializer):
    variant = serializers.PrimaryKeyRelatedField(queryset=Variant.objects.all())
    text = serializers.CharField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    images = serializers.ListField(
        child=serializers.FileField(), required=False, default=list
    )

    def validate_rating(self, value):
        if value < 1.0 or value > 5.0:
            raise serializers.ValidationError("Rating must be between 1.0 and 5.0")
        return value


class CommentStatusSerializer(serializers.Serializer):
    can_comment = serializers.BooleanField()
    has_commented = serializers.BooleanField()


class CommentUpdateSerializer(serializers.Serializer):
    text = serializers.CharField(required=False)
    rating = serializers.DecimalField(
        max_digits=3, decimal_places=1, required=False
    )
    images = serializers.ListField(
        child=serializers.FileField(), required=False, default=list
    )

    def validate_rating(self, value):
        if value < 1.0 or value > 5.0:
            raise serializers.ValidationError("Rating must be between 1.0 and 5.0")
        return value
