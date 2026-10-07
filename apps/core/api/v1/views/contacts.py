from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.v1.serializers.contacts import ContactSerializer
from apps.core.api.v1.services.contacts import ContactService


class ContactView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=ContactSerializer,
        tags=["Contact"],
        operation_description="Contact create",
    )
    def post(self, request, *args, **kwargs):
        return ContactService(request=request).create_contact(*args, **kwargs)
