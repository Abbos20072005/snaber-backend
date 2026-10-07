from modeltranslation.translator import TranslationOptions, translator

from apps.company.models import Company, CompanyGallery, Feature


class CompanyTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Company, CompanyTranslationOptions)


class CompanyGalleryTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(CompanyGallery, CompanyGalleryTranslationOptions)


class FeatureTranslationOptions(TranslationOptions):
    fields = ("name",)


translator.register(Feature, FeatureTranslationOptions)
