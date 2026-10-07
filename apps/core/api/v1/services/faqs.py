from rest_framework import status

from apps.core.api.v1.repositories.faqs import FaqRepository
from apps.core.api.v1.serializers.faqs import (
    FaqCreateUpdateSerializer,
    FaqListSerializer,
)
from apps.core.services import BaseService


class FaqService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = FaqRepository()

    def get_faqs(self, *args, **kwargs):
        faqs = self.db.get_faqs()
        return self.get_response(
            faqs,
            FaqListSerializer,
            context={"request": self.request},
            many=True,
        )

    def create_faq(self, *args, **kwargs):
        serializer = FaqCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        faq = serializer.save()
        return self.get_response_object(
            faq, FaqListSerializer, context={"request": self.request}
        )

    def delete_faq(self, *args, **kwargs):
        faq = self.db.get_faq(faq_id=kwargs.get("id"))
        faq.delete()
        return self.get_response_object(
            context={"request": self.request},
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def get_faq(self, *args, **kwargs):
        faq = self.db.get_faq(faq_id=kwargs.get("id"))
        return self.get_response_object(
            faq, FaqListSerializer, context={"request": self.request}
        )

    def update_faq(self, *args, **kwargs):
        faq = self.db.get_faq(faq_id=kwargs.get("id"))
        serializer = FaqCreateUpdateSerializer(
            data=self.request.data,
            context={"request": self.request},
            partial=True,
            instance=faq,
        )
        serializer.is_valid(raise_exception=True)
        new_faq = serializer.save()
        return self.get_response_object(
            new_faq, FaqListSerializer, context={"request": self.request}
        )
