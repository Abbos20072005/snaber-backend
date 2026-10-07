from rest_framework import status

from apps.company.api.v1.repositories.galleries import CompanyGalleryRepository
from apps.company.api.v1.serializers.galleries import (
    CompanyGalleryCreateUpdateSerializer,
    CompanyGalleryListSerializer,
)
from apps.core.services import BaseService


class CompanyGalleryService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CompanyGalleryRepository()

    def create_gallery(self, *args, **kwargs):
        serializer = CompanyGalleryCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        gallery = serializer.save()
        return self.get_response_object(
            gallery,
            CompanyGalleryListSerializer,
            context={"request": self.request},
        )

    def get_company_gallery(self, *args, **kwargs):
        gallery = self.db.get_company_gallery(company_id=kwargs.get("id"))
        return self.get_response(
            gallery,
            CompanyGalleryListSerializer,
            context={"request": self.request},
            many=True,
        )

    def update_gallery(self, *args, **kwargs):
        gallery = self.db.get_gallery(gallery_id=kwargs.get("id"))
        serializer = CompanyGalleryCreateUpdateSerializer(
            data=self.request.data,
            context={"request": self.request},
            partial=True,
            instance=gallery,
        )
        serializer.is_valid(raise_exception=True)
        new_gallery = serializer.save()
        return self.get_response_object(
            new_gallery,
            CompanyGalleryListSerializer,
            context={"request": self.request},
        )

    def delete_gallery(self, *args, **kwargs):
        gallery = self.db.get_gallery(gallery_id=kwargs.get("id"))
        gallery.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def get_gallery(self, *args, **kwargs):
        gallery = self.db.get_gallery(gallery_id=kwargs.get("id"))
        return self.get_response_object(
            gallery,
            CompanyGalleryListSerializer,
            context={"request": self.request},
        )
