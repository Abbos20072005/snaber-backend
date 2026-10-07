from django.conf import settings
from rest_framework import serializers

from apps.company.api.v1.serializers.companies import CompanyListSerializer
from apps.order.api.v1.serializers.order import RFQAttributeCreateSerializer
from apps.product.api.v1.serializers.products import (
    ProductListSerializer,
    VariantBaseSerializer,
)
from apps.product.api.v1.utils.cart import get_cart_item_total_price
from apps.product.api.v1.utils.currency import convert_price, get_target_currency
from apps.product.models import (
    AttributeValue,
    Cart,
    CartItem,
    Variant,
    VariantAttributeStock,
)


class CartCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Variant.objects.all(),
    )
    attribute_stock = serializers.PrimaryKeyRelatedField(
        queryset=VariantAttributeStock.objects.all(),
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField()
    attributes = RFQAttributeCreateSerializer(many=True, required=False)
    deadline = serializers.DateTimeField(required=False, allow_null=True)


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class CartAttributeStockValueSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    attribute_name = serializers.CharField(source="attribute.name")


class CartAttributeStockSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    attribute_values = CartAttributeStockValueSerializer(many=True)
    quantity = serializers.IntegerField()


class CartVariantSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    sku_variant = serializers.CharField()
    description = serializers.CharField()
    price_override = serializers.DecimalField(
        max_digits=14, decimal_places=2, allow_null=True
    )
    moq_override = serializers.IntegerField()
    stock_quantity = serializers.IntegerField()
    is_active = serializers.BooleanField()
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        last_media = obj.product_variant_medias.order_by("-id").first()
        if last_media and last_media.file:
            return last_media.file.url
        return None


class CartItemAttributeSerializer(serializers.Serializer):
    attribute = serializers.IntegerField()
    value_option = serializers.SerializerMethodField()
    value = serializers.CharField(required=False, allow_blank=True)

    def get_value_option(self, obj):
        vo_id = obj.get("value_option")
        if vo_id is None:
            return None
        cache = self.context.get("_value_option_cache", {})
        if vo_id in cache:
            return cache[vo_id]
        try:
            vo = AttributeValue.objects.only("id", "value", "image").get(id=vo_id)
            return {
                "id": vo.id,
                "value": vo.value,
                "image": vo.image.url if vo.image else None,
            }
        except AttributeValue.DoesNotExist:
            return None


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True, source="product.product")
    variant = VariantBaseSerializer(read_only=True, source="product")
    attribute_stock = CartAttributeStockSerializer(read_only=True)
    attributes = CartItemAttributeSerializer(many=True, read_only=True)
    deadline = serializers.DateTimeField(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "product",
            "variant",
            "attribute_stock",
            "attributes",
            "deadline",
            "quantity",
            "company",
            "total_price",
        )

    def to_representation(self, instance):
        if not self.context.get("_value_option_cache") and instance.attributes:
            vo_ids = {
                item["value_option"]
                for item in instance.attributes
                if isinstance(item.get("value_option"), int)
            }
            if vo_ids:
                vos = AttributeValue.objects.filter(id__in=vo_ids).only(
                    "id", "value", "image"
                )
                self.context["_value_option_cache"] = {
                    vo.id: {
                        "id": vo.id,
                        "value": vo.value,
                        "image": vo.image.url if vo.image else None,
                    }
                    for vo in vos
                }
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("total_price") is not None:
            data["total_price"] = convert_price(data["total_price"], target)
        return data

    def get_total_price(self, obj):
        return get_cart_item_total_price(obj)


class CartGroupSerializer(serializers.Serializer):
    company = CompanyListSerializer(allow_null=True)
    items = CartItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return sum(
            get_cart_item_total_price(item) or 0 for item in obj.get("items", [])
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("total_price") is not None:
            data["total_price"] = convert_price(data["total_price"], target)
        return data


class CartResponseSerializer(serializers.Serializer):
    groups = CartGroupSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    products = serializers.IntegerField()
    companies = serializers.IntegerField()
    currency = serializers.SerializerMethodField()

    def get_currency(self, obj):
        target = get_target_currency(self.context)
        return target if target else settings.BASE_CURRENCY

    def to_representation(self, instance):
        data = super().to_representation(instance)
        target = get_target_currency(self.context)
        if target and data.get("total_amount") is not None:
            data["total_amount"] = convert_price(data["total_amount"], target)
        return data


class CartListSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "groups")

    def get_groups(self, obj):
        items = obj.cartitem_set.select_related(
            "product", "company", "product__product__owner"
        ).all()
        grouped = {}
        for item in items:
            company = item.company or (
                item.product.product.owner if item.product else None
            )
            if company not in grouped:
                grouped[company] = []
            grouped[company].append(item)

        groups_data = []
        for company, company_items in grouped.items():
            company_serializer = (
                CompanyListSerializer(company, context=self.context)
                if company
                else None
            )
            items_serializer = CartItemSerializer(
                company_items, many=True, context=self.context
            )
            groups_data.append(
                {
                    "company": company_serializer.data if company_serializer else None,
                    "items": items_serializer.data,
                }
            )
        return groups_data


class CartSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "groups")

    def get_groups(self, obj):
        items = obj.cartitem_set.select_related(
            "product", "company", "product__product__owner"
        ).all()
        grouped = {}
        for item in items:
            company = item.company or (
                item.product.product.owner if item.product else None
            )
            if company not in grouped:
                grouped[company] = []
            grouped[company].append(item)

        groups_data = []
        for company, company_items in grouped.items():
            company_serializer = (
                CompanyListSerializer(company, context=self.context)
                if company
                else None
            )
            items_serializer = CartItemSerializer(
                company_items, many=True, context=self.context
            )
            groups_data.append(
                {
                    "company": company_serializer.data if company_serializer else None,
                    "items": items_serializer.data,
                }
            )
        return groups_data
