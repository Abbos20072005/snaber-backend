from django_countries import countries
from django_countries.fields import Country
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api.v1.serializers.countries import CountrySerializer


class CountryListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={200: CountrySerializer(many=True)},
        tags=["Core"],
        operation_description="API to get all countries",
    )
    def get(self, request, *args, **kwargs):
        data = [{"code": code, "name": Country(code).name} for code, _ in countries]
        serializer = CountrySerializer(data, many=True)
        return Response(serializer.data)
