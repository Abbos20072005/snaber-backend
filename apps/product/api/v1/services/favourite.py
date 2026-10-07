import uuid

from rest_framework import status

from apps.core.exceptions import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException,
)
from apps.core.services import BaseService
from apps.product.api.v1.repositories.favourite import FavouriteRepository
from apps.product.api.v1.serializers.favourite import (
    FavouriteCreateSerializer,
    FavouriteListSerializer,
)


class FavouriteService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = FavouriteRepository()

    def _get_session_key(self):
        session_key = self.request.COOKIES.get("sessionid")
        if not session_key:
            session_key = str(uuid.uuid4())
        return session_key

    def post(self, *args, **kwargs):
        serializer = FavouriteCreateSerializer(
            data=self.request.data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data.get("product_id")
        is_favourite = serializer.validated_data.get("is_favourite")

        user = self.request.user if self.request.user.is_authenticated else None
        session_key = self._get_session_key() if not user else ""

        product_model = self.db.get_product(product_id)

        if not product_model:
            raise ObjectNotFoundException("Object not found")

        if is_favourite:
            if self.db.favourite_exists(
                product_id=product_id, user=user, session_key=session_key
            ):
                raise ObjectAlreadyExistsException("Object already exists")
            favourite = self.db.create_favourite(
                product=product_model,
                user=user,
                session_key=session_key,
            )

            response = self.get_response(
                favourite,
                FavouriteListSerializer,
                context={"request": self.request},
                status_code=status.HTTP_201_CREATED,
            )
        else:
            self.db.delete_favourite(
                product_id=product_id, user=user, session_key=session_key
            )
            response = self.get_response_object(
                context={"request": self.request.data},
                status_code=status.HTTP_200_OK,
            )

        if not user:
            response.set_cookie(
                "sessionid",
                session_key,
                max_age=60 * 60 * 24 * 10,
                httponly=True,
                samesite="Lax",
            )

        return response

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            favourite = self.db.get_favourite_list(user=self.request.user)
        else:
            session_key = self.request.COOKIES.get("sessionid")
            favourite = self.db.get_favourite_list(session_key=session_key)

        return self.get_response(
            favourite,
            FavouriteListSerializer,
            context={"request": self.request},
            many=True,
            status_code=status.HTTP_200_OK,
        )
