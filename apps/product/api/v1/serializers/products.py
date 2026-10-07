from django.conf import settings
from rest_framework import serializers

from apps.company.api.v1.serializers.companies import CompanySerializer
from apps.company.models import Company
from apps.product.api.v1.serializers.categories import CategoryListSerializer
from apps.product.api.v1.utils.currency import convert_price, get_target_currency
from apps.product.models import (
    Attribute,
    Product,
    VariantMedia,
)


class CategoryBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class UnitBaseSerialzer(serializers.Serializer):
    id = serializers.IntegerField()
    unit = serializers.CharField()


class IndustryBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CreatorBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)


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


class VariantMediaBaseSerializer(serializers.Serializer):
    product_variant = serializers.IntegerField(source="product_variant.id")
    file = serializers.FileField()
    product_media_type = serializers.ChoiceField(choices=VariantMedia.MediaType.choices)


class CharacteristicBaseSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class AttributeValueStockBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()


class AttributeStockBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute_values = AttributeValueStockBaseSerializer(many=True)
    quantity = serializers.IntegerField()


class VariantBaseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    variant_constructor_id = serializers.SerializerMethodField()
    description = serializers.CharField()
    moq_override = serializers.IntegerField()
    price_override = serializers.DecimalField(max_digits=14, decimal_places=2)
    sku_variant = serializers.CharField()
    stock_quantity = serializers.IntegerField()
    attributes = ProductAttributeValueSerializer(
        many=True, source="product_attribute_values"
    )
    medias = VariantMediaBaseSerializer(many=True, source="product_variant_medias")
    characteristics = CharacteristicBaseSerializer(
        many=True, source="characteristic_set"
    )
    attribute_stocks = AttributeStockBaseSerializer(many=True, read_only=True)
    is_active = serializers.BooleanField()

    def get_variant_constructor_id(self, obj):
        vc = obj.variant_constructors.first()
        return vc.id if vc else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("price_override") is not None:
            data["price_override"] = convert_price(data["price_override"], target)
        return data


class ProductListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField()
    product_type = serializers.ChoiceField(choices=Product.ProductType.choices)
    price_type = serializers.ChoiceField(choices=Product.PriceType.choices)
    price_min = serializers.DecimalField(max_digits=55, decimal_places=2)
    price_max = serializers.DecimalField(max_digits=55, decimal_places=2)
    image = serializers.FileField()
    images = serializers.SerializerMethodField()
    moq = serializers.IntegerField()
    moq_unit = UnitBaseSerialzer()
    lead_time_min = serializers.IntegerField()
    lead_time_max = serializers.IntegerField()
    # Product may be created without a company (feature disabled for the frontend)
    industries = IndustryBaseSerializer(
        many=True, source="owner.industries", default=[]
    )
    category = serializers.IntegerField(source="category_id")
    variants = serializers.IntegerField(source="product_variants.count")
    view_count = serializers.IntegerField()
    creator = CreatorBaseSerializer(
        read_only=True, allow_null=True, default=None
    )
    company = CompanySerializer(source="owner", allow_null=True, default=None)
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    currency = serializers.SerializerMethodField()

    def get_currency(self, obj):
        target = get_target_currency(self.context)
        return target if target else settings.BASE_CURRENCY

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target:
            if data.get("price_min") is not None:
                data["price_min"] = convert_price(data["price_min"], target)
            if data.get("price_max") is not None:
                data["price_max"] = convert_price(data["price_max"], target)
        return data

    def get_images(self, obj):
        request = self.context.get("request")
        urls = []

        medias = VariantMedia.objects.filter(
            product_variant__product=obj,
            product_media_type=VariantMedia.MediaType.PHOTO,
        )[:10]
        for media in medias:
            if media.file:
                url = media.file.url
                if request is not None:
                    url = request.build_absolute_uri(url)
                urls.append(url)

        return urls


class CompanyProductListSerializer(ProductListSerializer):
    category = CategoryBaseSerializer()


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Product
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


class ProductDetailSerializer(ProductListSerializer):
    product_id = serializers.IntegerField(source="pk")
    constructor_id = serializers.SerializerMethodField()
    category = CategoryBaseSerializer()
    variants = VariantBaseSerializer(many=True, source="product_variants")
    moderator_comment = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def _get_constructor(self, obj):
        return getattr(obj, "product_constructor", None)

    def get_constructor_id(self, obj):
        constructor = self._get_constructor(obj)
        return constructor.id if constructor else None

    def get_moderator_comment(self, obj):
        constructor = self._get_constructor(obj)
        return constructor.moderator_comment if constructor else ""

    def get_status(self, obj):
        constructor = self._get_constructor(obj)
        return constructor.status if constructor else None


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="product.id")
    name = serializers.CharField(source="product.name")
    media = serializers.SerializerMethodField()
    owner = serializers.IntegerField(read_only=True, source="product.owner.id")
    category = serializers.IntegerField(read_only=True, source="product.category.id")

    def get_media(self, obj):
        first = obj.product_variant_medias.first()
        if not first or not first.file:
            return None
        request = self.context.get("request")
        url = first.file.url
        return request.build_absolute_uri(url) if request else url


class DraftProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id",)


class GlobalSearchSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    categories = CategoryListSerializer(many=True)
    companies = CompanySerializer(many=True)
