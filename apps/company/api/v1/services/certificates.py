from rest_framework import status

from apps.company.api.v1.repositories.certificates import CompanyCertificateRepository
from apps.company.api.v1.serializers.certificates import (
    CompanyCertificateCreateUpdateSerializer,
    CompanyCertificateListSerializer,
)
from apps.core.services import BaseService


class CompanyCertificateService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CompanyCertificateRepository()

    def create_certificate(self, *args, **kwargs):
        serializer = CompanyCertificateCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        certificate = serializer.save()
        return self.get_response_object(
            certificate,
            CompanyCertificateListSerializer,
            context={"request": self.request},
        )

    def get_company_certificate(self, *args, **kwargs):
        certificates = self.db.get_company_certificate(company_id=kwargs.get("id"))
        return self.get_response(
            certificates,
            CompanyCertificateListSerializer,
            context={"request": self.request},
            many=True,
        )

    def update_certificate(self, *args, **kwargs):
        certificate = self.db.get_certificate(certificate_id=kwargs.get("id"))
        serializer = CompanyCertificateCreateUpdateSerializer(
            data=self.request.data,
            context={"request": self.request},
            partial=True,
            instance=certificate,
        )
        serializer.is_valid(raise_exception=True)
        new_certificate = serializer.save()
        return self.get_response_object(
            new_certificate,
            CompanyCertificateListSerializer,
            context={"request": self.request},
        )

    def delete_certificate(self, *args, **kwargs):
        certificate = self.db.get_certificate(certificate_id=kwargs.get("id"))
        certificate.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def get_certificate(self, *args, **kwargs):
        certificate = self.db.get_certificate(certificate_id=kwargs.get("id"))
        return self.get_response_object(
            certificate,
            CompanyCertificateListSerializer,
            context={"request": self.request},
        )
