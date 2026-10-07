import json

from rest_framework import serializers

from apps.company.api.v1.serializers.companies import CompanySerializer
from apps.company.models import Company
from apps.core.exceptions import ObjectNotFoundException
from apps.product.api.v1.serializers.products import (
    CategoryBaseSerializer,
    CharacteristicBaseSerializer,
    CreatorBaseSerializer,
    IndustryBaseSerializer,
    ProductAttributeValueSerializer,
    UnitBaseSerialzer,
)
from apps.product.api.v1.utils.currency import convert_price, get_target_currency
from apps.product.models import (
    Attribute,
    AttributeValue,
    CharacteristicConstructor,
    Product,
    ProductAttributeValueConstructor,
    ProductConstructor,
    VariantAttributeStockConstructor,
    VariantConstructor,
    VariantMediaConstructor,
)


class ProductConstructorCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = ProductConstructor
        fields = (
            "id",
            "owner",
            "name_uz",
            "name_ru",
            "name_en",
            "category",
            "sku",
            "image",
            "product_type",
            "price_type",
            "price_min",
            "price_max",
            "moq",
            "moq_unit",
            "lead_time_min",
            "lead_time_max",
            "is_active",
        )


class ProductConstructorListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    status = serializers.CharField()
    product_type = serializers.ChoiceField(choices=Product.ProductType.choices)
    price_type = serializers.ChoiceField(choices=Product.PriceType.choices)
    price_min = serializers.DecimalField(max_digits=55, decimal_places=2)
    price_max = serializers.DecimalField(max_digits=55, decimal_places=2)
    image = serializers.FileField()
    moq = serializers.IntegerField()
    moq_unit = serializers.IntegerField(source="moq_unit_id")
    lead_time_min = serializers.IntegerField()
    lead_time_max = serializers.IntegerField()
    moderator_comment = serializers.CharField()
    original_product = serializers.IntegerField(source="original_product_id")
    creator = CreatorBaseSerializer(
        read_only=True, allow_null=True, default=None
    )
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("price_min") is not None:
                data["price_min"] = convert_price(data["price_min"], target)
            if data.get("price_max") is not None:
                data["price_max"] = convert_price(data["price_max"], target)
        return data


class ConstructorReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductConstructor
        fields = ("id", "status", "moderator_comment")


class _AttributeValueInputSerializer(serializers.Serializer):
    attribute = serializers.IntegerField()
    value = serializers.IntegerField()


class _CharacteristicInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class _CharacteristicConstructorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    value = serializers.CharField()


class _VariantMediaConstructorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    file = serializers.FileField()
    media_type = serializers.CharField()


class _AttributeConstructorOutputSerializer(serializers.Serializer):
    attribute = serializers.IntegerField(source="attribute_id")
    attribute_value = serializers.IntegerField(source="attribute_value_id")


class VariantConstructorCreateUpdateSerializer(serializers.ModelSerializer):
    attributes = _AttributeValueInputSerializer(
        many=True, write_only=True, required=False
    )
    images = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )
    characteristics = _CharacteristicInputSerializer(
        many=True, write_only=True, required=False
    )
    attribute_stocks = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )

    class Meta:
        model = VariantConstructor
        fields = (
            "id",
            "product_constructor",
            "description_uz",
            "description_ru",
            "description_en",
            "sku_variant",
            "price_override",
            "moq_override",
            "stock_quantity",
            "attributes",
            "images",
            "characteristics",
            "attribute_stocks",
            "is_active",
        )

    def _set_attributes(self, variant_constructor, attributes_data):
        ProductAttributeValueConstructor.objects.filter(
            variant_constructor=variant_constructor
        ).delete()
        items = []
        for item in attributes_data:
            attribute = Attribute.objects.filter(id=item["attribute"]).first()
            if not attribute:
                raise ObjectNotFoundException(
                    message="Attribute not found", message_key="attribute_not_found"
                )
            value = AttributeValue.objects.filter(id=item["value"]).first()
            if not value:
                raise ObjectNotFoundException(
                    message="Attribute value not found",
                    message_key="attribute_value_not_found",
                )
            items.append(
                ProductAttributeValueConstructor(
                    variant_constructor=variant_constructor,
                    attribute=attribute,
                    attribute_value=value,
                )
            )
        ProductAttributeValueConstructor.objects.bulk_create(items)

    def _set_images(self, variant_constructor, images_data):
        user = self.context["request"].user
        variant_constructor.variant_media_constructors.all().delete()
        VariantMediaConstructor.objects.bulk_create(
            [
                VariantMediaConstructor(
                    user=user,
                    variant_constructor=variant_constructor,
                    file=image,
                )
                for image in images_data
            ]
        )

    def _set_characteristics(self, variant_constructor, characteristics_data):
        CharacteristicConstructor.objects.filter(
            variant_constructor=variant_constructor
        ).delete()
        CharacteristicConstructor.objects.bulk_create(
            [
                CharacteristicConstructor(
                    variant_constructor=variant_constructor, **item
                )
                for item in characteristics_data
            ]
        )

    def _set_attribute_stocks(self, variant_constructor, stocks_data):
        variant_constructor.attribute_stock_constructors.all().delete()
        for item in stocks_data:
            value_ids = item.get("attribute_values", [])
            quantity = item.get("quantity", 0)
            values = AttributeValue.objects.filter(id__in=value_ids)
            if values.count() != len(value_ids):
                raise ObjectNotFoundException(
                    message="One or more attribute values not found",
                    message_key="attribute_value_not_found",
                )
            stock = VariantAttributeStockConstructor.objects.create(
                variant_constructor=variant_constructor,
                quantity=quantity,
            )
            stock.attribute_values.set(values)

    def to_internal_value(self, data):
        if hasattr(data, "getlist"):
            plain = {}
            for key in data:
                values = data.getlist(key)
                plain[key] = values if key == "images" or len(values) > 1 else values[0]
            data = plain
        for field in ("attributes", "characteristics", "attribute_stocks"):
            if isinstance(data.get(field), str):
                try:
                    data[field] = json.loads(data[field])
                except json.JSONDecodeError as err:
                    raise serializers.ValidationError(
                        {field: "Must be a valid JSON string."}
                    ) from err
        return super().to_internal_value(data)

    def create(self, validated_data):
        attributes_data = validated_data.pop("attributes", [])
        images_data = validated_data.pop("images", [])
        characteristics_data = validated_data.pop("characteristics", [])
        stocks_data = validated_data.pop("attribute_stocks", [])
        variant_constructor = super().create(validated_data)
        self._set_attributes(variant_constructor, attributes_data)
        self._set_images(variant_constructor, images_data)
        self._set_characteristics(variant_constructor, characteristics_data)
        if stocks_data:
            self._set_attribute_stocks(variant_constructor, stocks_data)
        return variant_constructor

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop("attributes", [])
        images_data = validated_data.pop("images", [])
        characteristics_data = validated_data.pop("characteristics", [])
        stocks_data = validated_data.pop("attribute_stocks", [])
        variant_constructor = super().update(instance, validated_data)
        if attributes_data:
            self._set_attributes(variant_constructor, attributes_data)
        if images_data:
            self._set_images(variant_constructor, images_data)
        if characteristics_data:
            self._set_characteristics(variant_constructor, characteristics_data)
        if stocks_data:
            self._set_attribute_stocks(variant_constructor, stocks_data)
        return variant_constructor


class _AttributeValueStockConstructorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class _AttributeStockConstructorOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute_values = _AttributeValueStockConstructorOutputSerializer(many=True)
    quantity = serializers.IntegerField()


class VariantConstructorListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product_constructor = serializers.IntegerField(source="product_constructor_id")
    description = serializers.CharField()
    sku_variant = serializers.CharField()
    price_override = serializers.DecimalField(max_digits=14, decimal_places=2)
    moq_override = serializers.IntegerField()
    stock_quantity = serializers.IntegerField()
    is_active = serializers.BooleanField()
    characteristics = _CharacteristicConstructorOutputSerializer(
        many=True, source="characteristic_constructors"
    )
    medias = _VariantMediaConstructorOutputSerializer(
        many=True, source="variant_media_constructors"
    )
    attributes = _AttributeConstructorOutputSerializer(
        many=True, source="attribute_value_constructors"
    )
    attribute_stocks = _AttributeStockConstructorOutputSerializer(
        many=True, source="attribute_stock_constructors"
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("price_override") is not None:
            data["price_override"] = convert_price(data["price_override"], target)
        return data


class _VariantMediaConstructorDetailSerializer(serializers.Serializer):
    product_variant = serializers.IntegerField(source="variant_constructor.id")
    file = serializers.FileField()
    product_media_type = serializers.CharField(source="media_type")


class VariantConstructorDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant_constructor_id = serializers.IntegerField(source="id")
    description = serializers.CharField()
    description_uz = serializers.CharField()
    description_en = serializers.CharField()
    description_ru = serializers.CharField()
    moq_override = serializers.IntegerField()
    price_override = serializers.DecimalField(max_digits=14, decimal_places=2)
    sku_variant = serializers.CharField()
    stock_quantity = serializers.IntegerField()
    attributes = ProductAttributeValueSerializer(
        many=True, source="attribute_value_constructors"
    )
    medias = _VariantMediaConstructorDetailSerializer(
        many=True, source="variant_media_constructors"
    )
    characteristics = CharacteristicBaseSerializer(
        many=True, source="characteristic_constructors"
    )
    attribute_stocks = _AttributeStockConstructorOutputSerializer(
        many=True, source="attribute_stock_constructors"
    )
    is_active = serializers.BooleanField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("price_override") is not None:
            data["price_override"] = convert_price(data["price_override"], target)
        return data


class ProductConstructorDetailSerializer(serializers.Serializer):
    constructor_id = serializers.IntegerField(source="id")
    product_id = serializers.IntegerField(source="original_product_id")
    moderator_comment = serializers.CharField()
    status = serializers.CharField()
    original_product = serializers.IntegerField(source="original_product_id")
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_en = serializers.CharField()
    name_ru = serializers.CharField()
    sku = serializers.CharField()
    product_type = serializers.ChoiceField(choices=Product.ProductType.choices)
    price_type = serializers.ChoiceField(choices=Product.PriceType.choices)
    price_min = serializers.DecimalField(max_digits=55, decimal_places=2)
    price_max = serializers.DecimalField(max_digits=55, decimal_places=2)
    image = serializers.FileField()
    moq = serializers.IntegerField()
    moq_unit = UnitBaseSerialzer()
    lead_time_min = serializers.IntegerField()
    lead_time_max = serializers.IntegerField()
    # Constructor may be created without a company (feature disabled for the frontend)
    industries = IndustryBaseSerializer(
        many=True, source="owner.industries", default=[]
    )
    creator = CreatorBaseSerializer(
        read_only=True, allow_null=True, default=None
    )
    company = CompanySerializer(source="owner", allow_null=True, default=None)
    category = CategoryBaseSerializer()
    variants = VariantConstructorDetailSerializer(
        many=True, source="variant_constructors"
    )
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("price_min") is not None:
                data["price_min"] = convert_price(data["price_min"], target)
            if data.get("price_max") is not None:
                data["price_max"] = convert_price(data["price_max"], target)
        return data
