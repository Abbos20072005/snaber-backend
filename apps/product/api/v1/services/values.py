from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.filters.values import AttributeValueFilter
from apps.product.api.v1.repositories.values import AttributeValueRepository
from apps.product.api.v1.serializers.values import (
    AttributeValueCreateSerializer,
    AttributeValueListSerializer,
)


class AttributeValueService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = AttributeValueRepository()

    def get_values(self, *args, **kwargs):
        values = self.db.get_values()
        filtered_values = AttributeValueFilter(
            data=self.request.query_params,
            queryset=values,
            request=self.request,
        ).qs
        return self.get_paginated_response(
            filtered_values,
            AttributeValueListSerializer,
            context={"request": self.request},
        )

    def create_value(self, *args, **kwargs):
        serializer = AttributeValueCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        value = serializer.save()
        return self.get_response_object(
            value,
            AttributeValueListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def update_value(self, *args, **kwargs):
        value = self.db.get_value(value_id=kwargs.get("id"))
        serializer = AttributeValueCreateSerializer(
            data=self.request.data,
            instance=value,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        updated_value = serializer.save()
        return self.get_response_object(
            updated_value,
            AttributeValueListSerializer,
            context={"request": self.request},
        )

    def delete_value(self, *args, **kwargs):
        value = self.db.get_value(value_id=kwargs.get("id"))
        value.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )
