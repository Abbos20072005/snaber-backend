from django.contrib import admin

from apps.product.models import (
    Attribute,
    AttributeValue,
    Cart,
    CartItem,
    Category,
    Favourite,
    Product,
    ProductAttributeValue,
    ProductCharacteristic,
    ProductImage,
    Unit,
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


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 1


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 0
    autocomplete_fields = ["attribute", "attribute_value"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "sku",
        "price",
        "discount_percent",
        "stock_quantity",
        "is_active",
    )
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku")
    inlines = [
        ProductImageInline,
        ProductCharacteristicInline,
        ProductAttributeValueInline,
    ]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "attribute_type", "is_filterable")
    list_filter = ("attribute_type", "is_filterable")
    search_fields = ("name",)


@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("id", "attribute__name", "value")
    search_fields = ("value", "attribute__name")


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
    list_display = ("id", "cart", "product", "quantity")
    list_filter = ("cart", "product")
    search_fields = ("cart", "product")
    autocomplete_fields = ["product", "cart"]
