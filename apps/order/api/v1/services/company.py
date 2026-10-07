from apps.company.models import Company
from apps.core.exceptions import ObjectNotFoundException
from apps.core.services import BaseService
from apps.order.api.v1.repositories.company import CompanyOrderRepository
from apps.order.api.v1.serializers.order import OrderListSerializer


class CompanyOrderService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CompanyOrderRepository()

    def get(self, pk):
        company = Company.objects.filter(id=pk).first()
        if not company:
            raise ObjectNotFoundException(message="Company not found")

        orders = self.db.get(pk, query_params=self.request.query_params)
        return self.get_paginated_response(orders, OrderListSerializer)
