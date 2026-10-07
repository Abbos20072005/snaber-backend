from apps.core.api.v1.serializers.currency import CurrencySerializer
from apps.core.api.v1.repositories.currency import CurrencyRepository
from apps.core.services import BaseService


class CurrencyService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CurrencyRepository()

    def get_currencies(self, *args, **kwargs):
        currencies = self.db.get_currencies()
        return self.get_response(
            currencies, CurrencySerializer, context={"request": self.request}, many=True
        )
