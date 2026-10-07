from django.conf import settings

from apps.core.currency_service import CurrencyService

_service = None


def get_currency_service():
    global _service
    if _service is None:
        _service = CurrencyService()
    return _service


def convert_price(price, target_currency):
    """Convert a single price value from BASE_CURRENCY to target."""
    if price is None or not target_currency:
        return price
    if target_currency == settings.BASE_CURRENCY:
        return price
    return get_currency_service().convert(
        price, settings.BASE_CURRENCY, target_currency
    )


def get_target_currency(context):
    request = context.get("request")
    if not request:
        return None
    if request.user.is_authenticated:
        return request.user.currency
    # Guest currency choice (catalog-only storefront has no login).
    guest_currency = request.query_params.get("currency")
    if guest_currency in ("USD", "EUR", "RUB", "CNY", "UZS"):
        return guest_currency
    # FEATURE DISABLED: USD guest default (store prices are in UZS).
    # return "USD"
    return settings.BASE_CURRENCY
