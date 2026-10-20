from apps.core.api.v1.repositories.legal import LegalClientsInfoRepository
from apps.core.api.v1.serializers.legal import (
    LegalClientsInfoListSerializer,
    LegalClientsInfoSerializer,
)
from apps.core.services import BaseService


class LegalClientsInfoService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = LegalClientsInfoRepository()

    def get_legal_info(self, *args, **kwargs):
        legal_info = self.db.get_legal_info()
        return self.get_response_object(
            legal_info,
            LegalClientsInfoListSerializer,
            context={"request": self.request},
        )

    def create_legal_info(self, *args, **kwargs):
        serializer = LegalClientsInfoSerializer(
            instance=self.db.get_legal_info(),
            data=self.request.data,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        legal_info = serializer.save()
        return self.get_response_object(
            legal_info,
            LegalClientsInfoListSerializer,
            context={"request": self.request},
        )
