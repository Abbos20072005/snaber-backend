from apps.core.currency_choices import CurrencyChoices


class CurrencyRepository:
    def get_currencies(self):
        return [{"code": code, "name": name} for code, name in CurrencyChoices.choices]
