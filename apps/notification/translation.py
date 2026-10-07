from modeltranslation.translator import TranslationOptions, translator

from apps.notification.models import Notification


class NotificationTranslationOptions(TranslationOptions):
    fields = ("title", "message")


translator.register(Notification, NotificationTranslationOptions)
