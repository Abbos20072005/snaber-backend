from rest_framework import status
from rest_framework.response import Response

from apps.core.services import BaseService
from apps.product.api.v1.filters.attributes import AttributeFilter
from apps.product.api.v1.repositories.attributes import (
    AttributeRepository,
)
from apps.product.api.v1.serializers.attributes import (
    AttributeCreateSerializer,
    AttributeFilterSerializer,
    AttributeListSerializer,
)


class AttributeService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = AttributeRepository()

    def get_attributes(self, *args, **kwargs):
        unfiltered_attributes = self.db.get_attributes()
        filtered_attributes = AttributeFilter(
            data=self.request.query_params,
            queryset=unfiltered_attributes,
            request=self.request,
        ).qs

        return self.get_response(
            filtered_attributes,
            AttributeListSerializer,
            context={"request": self.request},
            many=True,
        )

    def create_attribute(self, *args, **kwargs):
        serializer = AttributeCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        attribute = serializer.save()
        return self.get_response_object(
            attribute,
            AttributeListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def update_attribute(self, *args, **kwargs):
        attribute = self.db.get_attribute(attribute_id=kwargs.get("id"))
        serializer = AttributeCreateSerializer(
            data=self.request.data,
            instance=attribute,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        updated_attribute = serializer.save()
        return self.get_response_object(
            updated_attribute,
            AttributeListSerializer,
            context={"request": self.request},
        )

    def delete_attribute(self, *args, **kwargs):
        attribute = self.db.get_attribute(attribute_id=kwargs.get("id"))
        attribute.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def get_filterable_attributes(self, *args, **kwargs):
        category_id = self.request.query_params.get("category")
        category_id = int(category_id) if category_id else None
        attributes = self.db.get_filterable_attributes(category_id)
        price_min, price_max = self.db.get_price_range(category_id)
        attributes_data = AttributeFilterSerializer(
            attributes, many=True, context={"request": self.request}
        ).data
        return Response(
            {
                "price_min": price_min,
                "price_max": price_max,
                "attributes": attributes_data,
            }
        )
