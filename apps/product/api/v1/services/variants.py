from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.repositories.variants import ProductVariantRepository
from apps.product.api.v1.serializers.variants import (
    VariantCreateUpdateSerializer,
    VariantDetailSerializer,
    VariantListSerializer,
)


class VariantService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ProductVariantRepository()

    def create_variant(self, *args, **kwargs):
        serializer = VariantCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        variant = serializer.save()
        return self.get_response_object(
            variant,
            VariantListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def delete_variant(self, *args, **kwargs):
        variant = self.db.get_variant(kwargs.get("id"))
        variant.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def get_variant(self, *args, **kwargs):
        variant = self.db.get_variant(kwargs.get("id"))
        return self.get_response_object(
            variant, VariantDetailSerializer, context={"request": self.request}
        )
