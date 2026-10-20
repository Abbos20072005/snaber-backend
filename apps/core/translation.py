from modeltranslation.translator import TranslationOptions, translator

from apps.core.models import AboutUs, Faq, LegalClientsInfo


class FaqTranslationOptions(TranslationOptions):
    fields = ("name", "description")


translator.register(Faq, FaqTranslationOptions)


class AboutUsTranslationOptions(TranslationOptions):
    fields = ("information",)


translator.register(AboutUs, AboutUsTranslationOptions)


class LegalClientsInfoTranslationOptions(TranslationOptions):
    fields = ("information",)


translator.register(LegalClientsInfo, LegalClientsInfoTranslationOptions)
