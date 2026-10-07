from rest_framework import serializers

from apps.core.exceptions import ObjectNotFoundException
from apps.product.api.v1.utils.currency import convert_price, get_target_currency
from apps.product.models import (
    Attribute,
    AttributeValue,
    Characteristic,
    ProductAttributeValue,
    Variant,
    VariantAttributeStock,
    VariantMedia,
)


class ProductAttributeValueSerializer(serializers.Serializer):
    attribute = serializers.IntegerField()
    value = serializers.IntegerField()

    class Meta:
        ref_name = "VariantProductAttributeValue"


class CharacteristicSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class AttributeStockInputSerializer(serializers.Serializer):
    attribute_values = serializers.ListField(
        child=serializers.IntegerField(),
    )
    quantity = serializers.IntegerField(min_value=0)


class VariantCreateUpdateSerializer(serializers.ModelSerializer):
    attributes = ProductAttributeValueSerializer(
        many=True, write_only=True, required=False
    )
    images = serializers.ListField(child=serializers.FileField(), required=False)
    characteristics = CharacteristicSerializer(
        many=True, write_only=True, required=False
    )
    attribute_stocks = AttributeStockInputSerializer(
        many=True, write_only=True, required=False
    )

    class Meta:
        model = Variant
        fields = (
            "id",
            "product",
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

    def _set_attributes(self, variant, attributes_data):
        ProductAttributeValue.objects.filter(product=variant).delete()

        product_attribute_values = []

        for item in attributes_data:
            attribute_id = item.get("attribute")
            value_id = item.get("value")

            attribute = Attribute.objects.filter(id=attribute_id).first()
            if not attribute:
                raise ObjectNotFoundException(
                    message="Attribute not found", message_key="attribute_not_found"
                )

            value = AttributeValue.objects.filter(id=value_id).first()
            if not value:
                raise ObjectNotFoundException(
                    message="Attribute value not found",
                    message_key="attribute_value_not_found",
                )

            product_attribute_values.append(
                ProductAttributeValue(
                    product=variant,
                    attribute=attribute,
                    attribute_value=value,
                )
            )

        ProductAttributeValue.objects.bulk_create(product_attribute_values)

    def _set_images(self, variant, images_data):
        request = self.context.get("request")
        user = request.user

        old_medias = variant.product_variant_medias.all()
        old_medias.delete()

        new_medias = []
        for image in images_data:
            new_medias.append(
                VariantMedia(
                    user=user,
                    product_variant=variant,
                    file=image,
                )
            )
        VariantMedia.objects.bulk_create(new_medias)

    def _set_characteristics(self, variant, characteristics_data):
        Characteristic.objects.filter(product_variant=variant).delete()
        Characteristic.objects.bulk_create(
            [
                Characteristic(product_variant=variant, **item)
                for item in characteristics_data
            ]
        )

    def _set_attribute_stocks(self, variant, stocks_data):
        variant.attribute_stocks.all().delete()
        for item in stocks_data:
            value_ids = item["attribute_values"]
            values = AttributeValue.objects.filter(id__in=value_ids)
            if values.count() != len(value_ids):
                raise ObjectNotFoundException(
                    message="One or more attribute values not found",
                    message_key="attribute_value_not_found",
                )
            stock = VariantAttributeStock.objects.create(
                variant=variant,
                quantity=item["quantity"],
            )
            stock.attribute_values.set(values)

    def create(self, validated_data):
        attributes_data = validated_data.pop("attributes", [])
        images_data = validated_data.pop("images", [])
        characteristics_data = validated_data.pop("characteristics", [])
        stocks_data = validated_data.pop("attribute_stocks", [])
        variant = super().create(validated_data)
        self._set_attributes(variant, attributes_data)
        self._set_images(variant, images_data)
        self._set_characteristics(variant, characteristics_data)
        if stocks_data:
            self._set_attribute_stocks(variant, stocks_data)
        return variant

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop("attributes", [])
        images_data = validated_data.pop("images", [])
        characteristics_data = validated_data.pop("characteristics", [])
        stocks_data = validated_data.pop("attribute_stocks", [])
        variant = super().update(instance, validated_data)
        if attributes_data:
            self._set_attributes(variant, attributes_data)
        if images_data:
            self._set_images(variant, images_data)
        if characteristics_data:
            self._set_characteristics(variant, characteristics_data)
        if stocks_data:
            self._set_attribute_stocks(variant, stocks_data)
        return variant


class AttributeValueStockOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class AttributeStockOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute_values = AttributeValueStockOutputSerializer(many=True)
    quantity = serializers.IntegerField()


class VariantListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = serializers.IntegerField(source="product.id")
    description = serializers.CharField()
    sku_variant = serializers.CharField()
    options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    price_override = serializers.DecimalField(max_digits=14, decimal_places=2)
    moq_override = serializers.IntegerField()
    stock_quantity = serializers.IntegerField()
    attribute_stocks = AttributeStockOutputSerializer(many=True, read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    is_active = serializers.BooleanField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("price_override") is not None:
            data["price_override"] = convert_price(data["price_override"], target)
        return data


class VariantDetailSerializer(VariantListSerializer):
    description_uz = serializers.CharField()
    description_ru = serializers.CharField()
    description_en = serializers.CharField()
