from django.db import transaction
from rest_framework import serializers

from apps.product.api.v1.utils.family import field_error, validate_variant_options
from apps.product.models import (
    Attribute,
    AttributeValue,
    Product,
    ProductAttributeValue,
    ProductCharacteristic,
    ProductFamily,
)


class FamilyUnitSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField()


class FamilyAxisValueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class FamilyAxisSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    values = FamilyAxisValueSerializer(many=True, source="attribute_values")


class FamilyVariantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    image = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    discount_percent = serializers.IntegerField()
    final_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    stock_quantity = serializers.IntegerField()
    unit = FamilyUnitSerializer(allow_null=True)
    is_active = serializers.BooleanField()
    options = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()

    def get_image(self, obj):
        first = next(iter(obj.images.all()), None)
        if not first or not first.file:
            return None
        request = self.context.get("request")
        url = first.file.url
        return request.build_absolute_uri(url) if request else url

    def get_options(self, obj):
        axis_ids = self.context.get("axis_ids", [])
        return [
            {
                "attribute": item.attribute_id,
                "id": item.attribute_value_id,
                "value": item.attribute_value.value,
            }
            for item in obj.product_attribute_values.all()
            if item.attribute_id in axis_ids
        ]

    def get_values(self, obj):
        # Every option value of the variant, so the editor can change the axes and keep
        # the values that are not axes.
        return [item.attribute_value_id for item in obj.product_attribute_values.all()]


class FamilyDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_uz = serializers.CharField()
    name_ru = serializers.CharField()
    name_en = serializers.CharField()
    category = serializers.IntegerField(source="category_id")
    axes = FamilyAxisSerializer(many=True)
    variants = serializers.SerializerMethodField()

    def get_variants(self, obj):
        # Shoppers only see active variants, the admin editor sees all of them.
        include_inactive = self.context.get("include_inactive", False)
        axis_ids = [axis.id for axis in obj.axes.all()]
        variants = [
            variant
            for variant in obj.variants.all()
            if include_inactive or variant.is_active
        ]

        def option_ids(variant):
            by_axis = {
                item.attribute_id: item.attribute_value_id
                for item in variant.product_attribute_values.all()
            }
            return tuple(by_axis.get(axis_id, 0) for axis_id in axis_ids)

        variants.sort(key=lambda variant: (option_ids(variant), variant.id))
        return FamilyVariantSerializer(
            variants,
            many=True,
            context={**self.context, "axis_ids": axis_ids},
        ).data


class FamilyListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.IntegerField(source="category_id")
    variants_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class FamilyWriteSerializer(serializers.ModelSerializer):
    axes = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(), many=True, required=False
    )
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True, required=False, write_only=True
    )

    class Meta:
        model = ProductFamily
        fields = ("id", "name_uz", "name_ru", "name_en", "category", "axes", "products")
        extra_kwargs = {
            "name_uz": {"required": True, "allow_blank": False},
            "name_ru": {"required": False, "allow_blank": True},
            "name_en": {"required": False, "allow_blank": True},
        }

    def validate_category(self, category):
        if not category.is_leaf:
            raise serializers.ValidationError(
                "A family can only be added to the last-level category."
            )
        return category

    def validate(self, attrs):
        # The manager fills in Uzbek only; Russian and English default to it.
        for lang in ("ru", "en"):
            key = f"name_{lang}"
            current = getattr(self.instance, key, "") if self.instance else ""
            if attrs.get("name_uz") and not attrs.get(key) and not current:
                attrs[key] = attrs["name_uz"]

        category = attrs.get("category") or getattr(self.instance, "category", None)

        for axis in attrs.get("axes", []):
            if axis.category_id != category.id:
                raise field_error(
                    "axes",
                    "family_axis_category",
                    f"«{axis.name}» does not belong to this category.",
                )

        for product in attrs.get("products", []):
            if product.category_id != category.id:
                raise field_error(
                    "products",
                    "family_product_category",
                    f"«{product.name}» is in another category.",
                )
            taken = product.family_id and (
                not self.instance or product.family_id != self.instance.id
            )
            if taken:
                raise field_error(
                    "products",
                    "family_product_taken",
                    f"«{product.name}» is already in another family.",
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        axes = validated_data.pop("axes", [])
        products = validated_data.pop("products", [])
        validated_data["name"] = validated_data["name_en"]
        family = super().create(validated_data)
        family.axes.set(axes)
        Product.objects.filter(id__in=[product.id for product in products]).update(
            family=family
        )
        return family

    @transaction.atomic
    def update(self, instance, validated_data):
        axes = validated_data.pop("axes", None)
        products = validated_data.pop("products", [])
        family = super().update(instance, validated_data)
        if axes is not None:
            family.axes.set(axes)
        Product.objects.filter(id__in=[product.id for product in products]).update(
            family=family
        )
        return family


class VariantItemSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=100)
    price = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False, min_value=0
    )
    stock_quantity = serializers.IntegerField(required=False, min_value=0, default=0)
    attribute_values = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.select_related("attribute"), many=True
    )


class VariantBulkCreateSerializer(serializers.Serializer):
    base_product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    items = VariantItemSerializer(many=True, allow_empty=False)

    def validate(self, attrs):
        skus = [item["sku"].strip().lower() for item in attrs["items"]]
        if len(set(skus)) != len(skus):
            raise field_error(
                "items", "variant_sku_duplicate", "SKU values must be unique."
            )
        for item in attrs["items"]:
            if Product.objects.filter(sku__iexact=item["sku"].strip()).exists():
                raise field_error(
                    "items",
                    "variant_sku_taken",
                    f"SKU «{item['sku']}» is already used.",
                )
        return attrs

    @transaction.atomic
    def create_variants(self, family):
        base = self.validated_data["base_product"]
        axis_ids = {axis.id for axis in family.axes.all()}
        created = []

        for item in self.validated_data["items"]:
            values = item["attribute_values"]
            if any(value.attribute_id not in axis_ids for value in values):
                raise field_error(
                    "items",
                    "variant_axis_invalid",
                    "Options must belong to the axes of the family.",
                )
            # Sequential on purpose: each check sees the variants created before it, so
            # duplicate combinations inside one request are caught too.
            validate_variant_options(family, values)

            names = {
                lang: " — ".join(
                    [getattr(base, f"name_{lang}")]
                    + [getattr(value, f"value_{lang}") for value in values]
                )
                for lang in ("uz", "ru", "en")
            }
            variant = Product.objects.create(
                name=names["en"],
                name_uz=names["uz"],
                name_ru=names["ru"],
                name_en=names["en"],
                description=base.description_en,
                description_uz=base.description_uz,
                description_ru=base.description_ru,
                description_en=base.description_en,
                category=base.category,
                family=family,
                sku=item["sku"].strip(),
                unit=base.unit,
                price=item.get("price", base.price),
                discount_percent=base.discount_percent,
                stock_quantity=item["stock_quantity"],
                is_active=base.is_active,
            )
            ProductCharacteristic.objects.bulk_create(
                [
                    ProductCharacteristic(
                        product=variant,
                        name=row.name_en,
                        name_uz=row.name_uz,
                        name_ru=row.name_ru,
                        name_en=row.name_en,
                        value=row.value_en,
                        value_uz=row.value_uz,
                        value_ru=row.value_ru,
                        value_en=row.value_en,
                    )
                    for row in base.characteristics.all()
                ]
            )
            shared = [
                row.attribute_value
                for row in base.product_attribute_values.select_related(
                    "attribute", "attribute_value"
                )
                if row.attribute_id not in axis_ids
            ]
            self._set_attribute_values(variant, shared + list(values))
            created.append(variant)
        return created

    @staticmethod
    def _set_attribute_values(product, attribute_values):
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
