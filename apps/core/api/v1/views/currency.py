from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.v1.serializers.currency import CurrencySerializer
from apps.core.api.v1.services.currency import CurrencyService


class CurrencyListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CurrencySerializer(many=True)},
        tags=["Core"],
        operation_description="API to get all supported currencies",
    )
    def get(self, request, *args, **kwargs):
        return CurrencyService(request=request).get_currencies(*args, **kwargs)
