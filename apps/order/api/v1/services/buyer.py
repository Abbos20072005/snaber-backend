from apps.authentication.models import User
from apps.core.exceptions import ObjectNotFoundException
from apps.core.services import BaseService
from apps.order.api.v1.repositories.buyer import BuyerOrderRepository
from apps.order.api.v1.serializers.order import OrderListSerializer


class BuyerOrderService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = BuyerOrderRepository()

    def get(self, pk):
        buyer = User.objects.filter(id=pk).first()
        if not buyer or buyer.role != User.Roles.BUYER:
            raise ObjectNotFoundException(message="Buyer not found")

        orders = self.db.get(pk=pk, query_params=self.request.query_params)
        return self.get_paginated_response(orders, OrderListSerializer)
