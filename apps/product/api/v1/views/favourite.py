from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.product.api.v1.serializers.favourite import (
    FavouriteCreateSerializer,
    FavouriteListSerializer,
)
from apps.product.api.v1.services.favourite import (
    FavouriteService,
)


class FavouriteAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=FavouriteCreateSerializer,
        responses={200: FavouriteListSerializer},
        tags=["Favourite"],
    )
    def post(self, request, *args, **kwargs):
        return FavouriteService(request=request).post()

    @swagger_auto_schema(
        responses={200: FavouriteListSerializer},
        tags=["Favourite"],
    )
    def get(self, request, *args, **kwargs):
        return FavouriteService(request=request).get()
