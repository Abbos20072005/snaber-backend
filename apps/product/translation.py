from modeltranslation.translator import TranslationOptions, translator

from apps.product.models import (
    Attribute,
    Category,
    Product,
    ProductConstructor,
    Variant,
    VariantConstructor,
    AttributeValue, Unit,
)


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Category, CategoryTranslationOptions)


class ProductTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Product, ProductTranslationOptions)


class VariantTranslationOptions(TranslationOptions):
    fields = ("description",)


translator.register(Variant, VariantTranslationOptions)


class AttributeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Attribute, AttributeTranslationOptions)


class AttributeValueTranslationOptions(TranslationOptions):
    fields = ("value",)


translator.register(AttributeValue, AttributeValueTranslationOptions)


class ProductConstructorTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(ProductConstructor, ProductConstructorTranslationOptions)


class VariantConstructorTranslationOptions(TranslationOptions):
    fields = ("description",)


translator.register(VariantConstructor, VariantConstructorTranslationOptions)


class UnitTranslationOptions(TranslationOptions):
    fields = ("unit",)

translator.register(Unit, UnitTranslationOptions)