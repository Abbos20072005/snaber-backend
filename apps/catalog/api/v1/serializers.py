from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.catalog.models import Attribute, Category, Product


class AttributeRequirementSerializer(serializers.Serializer):
    key = serializers.CharField()
    value = serializers.CharField()


class AttributeListSerializer(serializers.ModelSerializer):
    requires = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ("key", "label", "requires")

    @extend_schema_field(AttributeRequirementSerializer(allow_null=True))
    def get_requires(self, obj):
        if obj.requires_attribute is None:
            return None
        return {"key": obj.requires_attribute.key, "value": obj.requires_value}


class CategoryTableSerializer(serializers.Serializer):
    """Leaf category specification table: grouping attribute and columns in order."""

    group_by = serializers.CharField(allow_null=True)
    columns = serializers.ListField(child=serializers.CharField())


def table_of(category):
    """Expects `table_group_by` and `table_columns__attribute` to be loaded."""
    columns = [column.attribute.key for column in category.table_columns.all()]
    if category.table_group_by is None and not columns:
        return None
    return {
        "group_by": category.table_group_by.key if category.table_group_by else None,
        "columns": columns,
    }


class CategoryRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("slug", "name", "icon")


class CategoryTreeSerializer(serializers.ModelSerializer):
    """One node of `GET catalog/tree/`; expects `tree` (CategoryTree) in the context."""

    product_count = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("slug", "name", "icon", "description", "product_count", "table", "children")

    def get_product_count(self, obj) -> int:
        return self.context["tree"].get_branch_count(obj.pk)

    @extend_schema_field(CategoryTableSerializer(allow_null=True))
    def get_table(self, obj):
        return table_of(obj)

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        children = self.context["tree"].get_children(obj.pk)
        return CategoryTreeSerializer(children, many=True, context=self.context).data


class CategoryCardSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("slug", "name", "icon", "description", "product_count")

    def get_product_count(self, obj) -> int:
        return self.context["tree"].get_branch_count(obj.pk)


class CategoryRetrieveSerializer(serializers.ModelSerializer):
    """Expects `tree` and `first_sku` in the context."""

    path = serializers.SerializerMethodField()
    trail = serializers.SerializerMethodField()
    is_leaf = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    first_sku = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "slug",
            "name",
            "icon",
            "description",
            "path",
            "trail",
            "is_leaf",
            "product_count",
            "table",
            "children",
            "first_sku",
        )

    def get_path(self, obj) -> list[str]:
        return self.context["tree"].get_slugs(obj.pk)

    @extend_schema_field(CategoryRelationSerializer(many=True))
    def get_trail(self, obj):
        return CategoryRelationSerializer(self.context["tree"].get_path(obj.pk), many=True).data

    def get_is_leaf(self, obj) -> bool:
        return self.context["tree"].is_leaf(obj.pk)

    def get_product_count(self, obj) -> int:
        return self.context["tree"].get_branch_count(obj.pk)

    @extend_schema_field(CategoryTableSerializer(allow_null=True))
    def get_table(self, obj):
        return table_of(obj)

    @extend_schema_field(CategoryCardSerializer(many=True))
    def get_children(self, obj):
        children = self.context["tree"].get_children(obj.pk)
        return CategoryCardSerializer(children, many=True, context=self.context).data

    def get_first_sku(self, obj) -> str | None:
        return self.context["first_sku"]


class ProductListSerializer(serializers.ModelSerializer):
    """Same shape as the frontend `Product` type plus the leaf category.

    `tree` kontekstda bo'lishi va `attribute_values__attribute` oldindan
    yuklangan bo'lishi kerak.
    """

    path = serializers.SerializerMethodField()
    category = CategoryRelationSerializer(read_only=True)
    attrs = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("sku", "name", "path", "price", "pack", "stock", "category", "attrs")

    def get_path(self, obj) -> list[str]:
        return self.context["tree"].get_slugs(obj.category_id)

    @extend_schema_field(serializers.DictField(child=serializers.CharField()))
    def get_attrs(self, obj):
        return {value.attribute.key: value.value for value in obj.attribute_values.all()}


class ProductRowSerializer(serializers.Serializer):
    """Same output as ProductListSerializer, built from `browse.ProductRow`.

    Ro'yxat uchun mahsulot va qiymatlari pool'da allaqachon yuklangan: ularni
    model sifatida qayta o'qish 500 talik sahifada soniyaga yaqin vaqt oladi.
    """

    sku = serializers.CharField()
    name = serializers.CharField()
    path = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    pack = serializers.IntegerField()
    stock = serializers.CharField()
    category = serializers.SerializerMethodField()
    attrs = serializers.DictField(child=serializers.CharField())

    def get_path(self, obj) -> list[str]:
        return self.context["tree"].get_slugs(obj.category_id)

    @extend_schema_field(CategoryRelationSerializer)
    def get_category(self, obj):
        # Sahifada bir kategoriya ko'p marta uchraydi; serializer har qatorda qayta qurilmasin.
        cache = self.context.setdefault("category_cache", {})
        if obj.category_id not in cache:
            cache[obj.category_id] = CategoryRelationSerializer(
                self.context["tree"].nodes[obj.category_id]
            ).data
        return cache[obj.category_id]


class ProductSpecSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    value = serializers.CharField()


class VariantOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    sku = serializers.CharField()
    selected = serializers.BooleanField()


class VariantGroupSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    value = serializers.CharField()
    options = VariantOptionSerializer(many=True)


class ProductRetrieveSerializer(ProductListSerializer):
    """Product page; expects `variants` and `variant_count` in the context."""

    trail = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()
    table = serializers.SerializerMethodField()
    variants = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            "trail",
            "specs",
            "table",
            "variants",
            "variant_count",
        )

    @extend_schema_field(CategoryRelationSerializer(many=True))
    def get_trail(self, obj):
        return CategoryRelationSerializer(
            self.context["tree"].get_path(obj.category_id), many=True
        ).data

    @extend_schema_field(ProductSpecSerializer(many=True))
    def get_specs(self, obj):
        # attribute_values xususiyat tartibida oldindan yuklangan.
        specs = [
            {"key": value.attribute.key, "label": value.attribute.label, "value": value.value}
            for value in obj.attribute_values.all()
        ]
        return ProductSpecSerializer(specs, many=True).data

    @extend_schema_field(CategoryTableSerializer(allow_null=True))
    def get_table(self, obj):
        return table_of(self.context["tree"].nodes[obj.category_id])

    @extend_schema_field(VariantGroupSerializer(many=True))
    def get_variants(self, obj):
        return VariantGroupSerializer(self.context["variants"], many=True).data

    def get_variant_count(self, obj) -> int:
        return self.context["variant_count"]


class FacetOptionSerializer(serializers.Serializer):
    value = serializers.CharField()
    count = serializers.IntegerField()
    selected = serializers.BooleanField()


class FacetSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    options = FacetOptionSerializer(many=True)


class FacetChildSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    icon = serializers.CharField()
    description = serializers.CharField()
    count = serializers.IntegerField()


class ProductFacetsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    facets = FacetSerializer(many=True)
    children = FacetChildSerializer(many=True)
    first_sku = serializers.CharField(allow_null=True)
