from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyChoices(models.TextChoices):
    USD = "USD", _("US Dollar")
    UZS = "UZS", _("Uzbek So'm")
    EUR = "EUR", _("Euro")
    RUB = "RUB", _("Russian Ruble")
    CNY = "CNY", _("Chinese Yuan")
