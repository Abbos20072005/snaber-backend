from django.contrib import admin

from apps.product.models import (
    Attribute,
    AttributeValue,
    Cart,
    CartItem,
    Category,
    Characteristic,
    CharacteristicConstructor,
    Favourite,
    Product,
    ProductAttributeValue,
    ProductAttributeValueConstructor,
    ProductConstructor,
    Unit,
    Variant,
    VariantAttributeStock,
    VariantAttributeStockConstructor,
    VariantConstructor,
    VariantMedia,
    VariantMediaConstructor,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "parent", "level", "is_leaf", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_leaf", "level")


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "unit")
    search_fields = ("unit",)
    list_filter = ("unit",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "category", "price_type", "is_active")
    list_filter = ("is_active", "price_type", "product_type")
    search_fields = ("name", "sku")


class VariantMediaInline(admin.TabularInline):
    model = VariantMedia
    extra = 1


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "sku_variant",
        "price_override",
        "stock_quantity",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("product__name", "sku_variant")

    inlines = [VariantMediaInline]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "attribute_type", "is_filterable")
    list_filter = ("attribute_type", "is_filterable")
    search_fields = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("id", "attribute__name", "value")
    search_fields = ("value", "attribute__name")


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "value")
    search_fields = ("id", "name", "value")


@admin.register(ProductAttributeValue)
class ProductAttributeValue(admin.ModelAdmin):
    list_display = ("id", "product", "attribute", "attribute_value")


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "session_key")
    list_filter = ("user", "product", "session_key")
    search_fields = ("user", "product", "session_key")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key")
    list_filter = ("user", "session_key")
    search_fields = ("user", "session_key")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "attribute_stock", "quantity", "company")
    list_filter = ("cart", "product", "company")
    search_fields = ("cart", "product")
    autocomplete_fields = ["product", "attribute_stock", "company", "cart"]


@admin.register(ProductConstructor)
class ProductConstructorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "category",
        "price_type",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_active", "price_type", "product_type")
    search_fields = ("name", "sku")


class VariantMediaConstructorInline(admin.TabularInline):
    model = VariantMediaConstructor
    extra = 1


@admin.register(VariantConstructor)
class VariantConstructorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_constructor",
        "sku_variant",
        "price_override",
        "stock_quantity",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("product_constructor__name", "sku_variant")
    inlines = [VariantMediaConstructorInline]


@admin.register(CharacteristicConstructor)
class CharacteristicConstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "value", "variant_constructor")
    search_fields = ("id", "name", "value")


@admin.register(ProductAttributeValueConstructor)
class ProductAttributeValueConstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "variant_constructor", "attribute", "attribute_value")


@admin.register(VariantAttributeStock)
class VariantAttributeStockAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "quantity")
    list_filter = ("variant",)
    search_fields = ("variant__product__name",)


@admin.register(VariantAttributeStockConstructor)
class VariantAttributeStockConstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "variant_constructor", "quantity")
    list_filter = ("variant_constructor",)
    search_fields = ("variant_constructor__product_constructor__name",)
