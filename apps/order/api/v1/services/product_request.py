import uuid

from rest_framework import status

from apps.authentication.models import User
from apps.core.exceptions import (
    ObjectNotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from apps.core.services import BaseService
from apps.order.api.v1.repositories.product_request import ProductRequestRepository
from apps.order.api.v1.serializers.product_request import (
    ProductRequestCreateSerializer,
    ProductRequestSerializer,
    ProductRequestUpdateSerializer,
    WantedProductSerializer,
)


class ProductRequestService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ProductRequestRepository()

    def get_all_requests(self):
        requests = self.db.get_all(
            self.request.user, query_params=self.request.query_params
        )
        return self.get_paginated_response(
            requests, ProductRequestSerializer, context={"request": self.request}
        )

    def get_wanted_products(self):
        products = self.db.get_wanted(self.request.query_params.get("search"))
        return self.get_paginated_response(products, WantedProductSerializer)

    def get_request(self, pk):
        product_request = self._get_accessible(pk)
        return self.get_response_object(
            product_request,
            ProductRequestSerializer,
            context={"request": self.request},
        )

    def create_request(self):
        serializer = ProductRequestCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        phone = data.pop("phone_number", None)
        buyer = self.request.user
        if not buyer.is_authenticated:
            buyer = self._get_or_create_buyer(phone)
        product_request = self.db.create(buyer, data)
        return self.get_response_object(
            {"result": {"id": product_request.id}},
            status_code=status.HTTP_201_CREATED,
        )

    def update_request(self, pk):
        product_request = self._get_accessible(pk)
        serializer = ProductRequestUpdateSerializer(
            product_request, data=self.request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_response_object(
            product_request,
            ProductRequestSerializer,
            context={"request": self.request},
        )

    @staticmethod
    def _get_or_create_buyer(phone):
        # A buyer without an account is registered by the phone number, no OTP.
        # The account is verified when the buyer logs in with the OTP later.
        if not phone:
            raise ValidationError(
                message="Enter your phone number", message_key="phone_required"
            )
        user = User.objects.filter(phone_number=phone).first()
        if not user:
            return User.objects.create_user(
                username=str(uuid.uuid4()), phone_number=phone
            )
        if user.is_blocked or not user.is_active:
            raise PermissionDeniedException(
                message="Your account is blocked.", message_key="user_blocked"
            )
        return user

    def _get_accessible(self, pk):
        product_request = self.db.get_by_id(pk)
        is_owner = product_request and product_request.buyer == self.request.user
        if not product_request or not (
            is_owner or self.request.user.role == User.Roles.ADMIN
        ):
            raise ObjectNotFoundException(
                message="Request not found", message_key="request_not_found"
            )
        return product_request
