from django.db import transaction
from rest_framework import serializers

from apps.product.api.v1.serializers.categories import CategoryListSerializer
from apps.product.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttributeValue,
    ProductCharacteristic,
    ProductImage,
)


class CategoryBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class UnitBaseSerialzer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField()


class AttributeValueBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class ProductAttributeValueSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="attribute.id")
    name = serializers.CharField(source="attribute.name")
    attribute_type = serializers.ChoiceField(
        source="attribute.attribute_type", choices=Attribute.Type.choices
    )
    category = serializers.IntegerField(source="attribute.category_id")
    is_filterable = serializers.BooleanField(source="attribute.is_filterable")
    value = AttributeValueBaseSerializer(source="attribute_value")


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "file", "position")


class CharacteristicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = (
            "id",
            "name",
            "value",
            "name_uz",
            "name_ru",
            "name_en",
            "value_uz",
            "value_ru",
            "value_en",
        )


class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    image = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    discount_percent = serializers.IntegerField()
    final_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    stock_quantity = serializers.IntegerField()
    unit = UnitBaseSerialzer(allow_null=True)
    category = serializers.IntegerField(source="category_id")
    is_active = serializers.BooleanField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    specifications = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()

    def _image_urls(self, obj):
        request = self.context.get("request")
        urls = []
        for image in obj.images.all():
            if image.file:
                url = image.file.url
                urls.append(request.build_absolute_uri(url) if request else url)
        return urls

    def get_image(self, obj):
        urls = self._image_urls(obj)
        return urls[0] if urls else None

    def get_images(self, obj):
        return self._image_urls(obj)[:10]

    def get_specifications(self, obj):
        # Filter attributes first, then the free-form characteristics, like the detail page.
        rows = [
            {"name": item.attribute.name, "value": item.attribute_value.value}
            for item in obj.product_attribute_values.all()
        ] + [{"name": item.name, "value": item.value} for item in obj.characteristics.all()]
        return rows[:6]


class ProductDetailSerializer(ProductListSerializer):
    category = CategoryBaseSerializer()
    description = serializers.CharField()
    medias = ProductImageSerializer(many=True, source="images")
    characteristics = CharacteristicDetailSerializer(many=True)
    attributes = ProductAttributeValueSerializer(
        many=True, source="product_attribute_values"
    )
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    description_uz = serializers.CharField()
    description_ru = serializers.CharField()
    description_en = serializers.CharField()


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    media = serializers.SerializerMethodField()
    category = serializers.IntegerField(read_only=True, source="category_id")

    def get_media(self, obj):
        first = obj.images.first()
        if not first or not first.file:
            return None
        request = self.context.get("request")
        url = first.file.url
        return request.build_absolute_uri(url) if request else url


class CharacteristicWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = (
            "name_uz",
            "name_ru",
            "name_en",
            "value_uz",
            "value_ru",
            "value_en",
        )
        extra_kwargs = {
            "name_uz": {"required": True, "allow_blank": False},
            "name_ru": {"required": False, "allow_blank": True},
            "name_en": {"required": False, "allow_blank": True},
            "value_uz": {"required": True, "allow_blank": False},
            "value_ru": {"required": False, "allow_blank": True},
            "value_en": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        for field in ("name", "value"):
            for lang in ("ru", "en"):
                key = f"{field}_{lang}"
                if not attrs.get(key):
                    attrs[key] = attrs[f"{field}_uz"]
        return attrs


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    characteristics = CharacteristicWriteSerializer(many=True, required=False)
    attribute_values = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(), many=True, required=False
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name_uz",
            "name_ru",
            "name_en",
            "description_uz",
            "description_ru",
            "description_en",
            "category",
            "sku",
            "unit",
            "price",
            "discount_percent",
            "stock_quantity",
            "is_active",
            "characteristics",
            "attribute_values",
        )
        extra_kwargs = {
            "name_uz": {"required": True, "allow_blank": False},
            "name_ru": {"required": False, "allow_blank": True},
            "name_en": {"required": False, "allow_blank": True},
            "description_uz": {"required": False, "allow_blank": True},
            "description_ru": {"required": False, "allow_blank": True},
            "description_en": {"required": False, "allow_blank": True},
        }

    def validate_category(self, category):
        if not category.is_leaf:
            raise serializers.ValidationError(
                "Product can only be added to the last-level category."
            )
        return category

    def validate(self, attrs):
        # The manager fills in Uzbek only; Russian and English default to it
        # until they are translated.
        for field in ("name", "description"):
            source = attrs.get(f"{field}_uz")
            if source is None:
                continue
            for lang in ("ru", "en"):
                key = f"{field}_{lang}"
                current = getattr(self.instance, key, "") if self.instance else ""
                if not attrs.get(key) and not current:
                    attrs[key] = source
        return attrs

    @staticmethod
    def _set_characteristics(product, characteristics):
        product.characteristics.all().delete()
        ProductCharacteristic.objects.bulk_create(
            [ProductCharacteristic(product=product, **item) for item in characteristics]
        )

    @staticmethod
    def _set_attribute_values(product, attribute_values):
        product.product_attribute_values.all().delete()
        ProductAttributeValue.objects.bulk_create(
            [
                ProductAttributeValue(
                    product=product,
                    attribute=value.attribute,
                    attribute_value=value,
                )
                for value in attribute_values
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        characteristics = validated_data.pop("characteristics", [])
        attribute_values = validated_data.pop("attribute_values", [])
        product = super().create(validated_data)
        self._set_characteristics(product, characteristics)
        self._set_attribute_values(product, attribute_values)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        characteristics = validated_data.pop("characteristics", None)
        attribute_values = validated_data.pop("attribute_values", None)
        product = super().update(instance, validated_data)
        if characteristics is not None:
            self._set_characteristics(product, characteristics)
        if attribute_values is not None:
            self._set_attribute_values(product, attribute_values)
        return product


class ProductImageUploadSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)


class GlobalSearchSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    categories = CategoryListSerializer(many=True)
