from modeltranslation.translator import TranslationOptions, translator

from apps.product.models import (
    Attribute,
    AttributeValue,
    Category,
    Product,
    ProductCharacteristic,
    Unit,
)


class CategoryTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Category, CategoryTranslationOptions)


class ProductTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Product, ProductTranslationOptions)


class ProductCharacteristicTranslationOptions(TranslationOptions):
    fields = ("name", "value")


translator.register(ProductCharacteristic, ProductCharacteristicTranslationOptions)


class AttributeTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Attribute, AttributeTranslationOptions)


class AttributeValueTranslationOptions(TranslationOptions):
    fields = ("value",)


translator.register(AttributeValue, AttributeValueTranslationOptions)


class UnitTranslationOptions(TranslationOptions):
    fields = ("unit",)


translator.register(Unit, UnitTranslationOptions)
