from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.filters.units import UnitFilter
from apps.product.api.v1.repositories.units import (
    UnitRepository,
)
from apps.product.api.v1.serializers.units import (
    UnitCreateSerializer,
    UnitListSerializer,
)


class UnitService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = UnitRepository()

    def get_units(self, *args, **kwargs):
        unfiltered_units = self.db.get_units(*args, **kwargs)
        filtered_units = UnitFilter(
            data=self.request.query_params,
            queryset=unfiltered_units,
            request=self.request,
        ).qs
        return self.get_response(
            filtered_units,
            UnitListSerializer,
            many=True,
            context={"request": self.request},
        )

    def create_unit(self, *args, **kwargs):
        serializer = UnitCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        unit = serializer.save()
        return self.get_response_object(
            unit,
            UnitListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def update_unit(self, *args, **kwargs):
        unit = self.db.get_unit(unit_id=kwargs.get("id"))
        serializer = UnitCreateSerializer(
            data=self.request.data,
            instance=unit,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        updated_unit = serializer.save()
        return self.get_response_object(
            updated_unit, UnitListSerializer, context={"request": self.request}
        )

    def delete_unit(self, *args, **kwargs):
        unit = self.db.get_unit(unit_id=kwargs.get("id"))
        unit.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )
