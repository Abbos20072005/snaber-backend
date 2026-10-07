from modeltranslation.translator import TranslationOptions, translator

from apps.core.models import Faq, AboutUs


class FaqTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Faq, FaqTranslationOptions)


class AboutUsTranslationOptions(TranslationOptions):
    fields = ("information",)


translator.register(AboutUs, AboutUsTranslationOptions)
