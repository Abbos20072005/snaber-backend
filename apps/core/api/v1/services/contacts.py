from rest_framework import status

from apps.core.api.v1.serializers.contacts import ContactSerializer
from apps.core.services import BaseService


class ContactService(BaseService):
    def __init__(self, request):
        super().__init__(request)

    def create_contact(self, *args, **kwargs):
        serializer = ContactSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()
        return self.get_response_object(
            contact,
            ContactSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )
