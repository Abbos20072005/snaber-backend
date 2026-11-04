from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.filters.families import FamilyFilter
from apps.product.api.v1.repositories.families import FamilyRepository
from apps.product.api.v1.serializers.families import (
    FamilyDetailSerializer,
    FamilyListSerializer,
    FamilyWriteSerializer,
    VariantBulkCreateSerializer,
)
from apps.product.api.v1.utils.family import field_error


class FamilyService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = FamilyRepository()
        self.context = {"request": request, "include_inactive": True}

    def get_families(self, *args, **kwargs):
        filtered_families = FamilyFilter(
            data=self.request.query_params,
            queryset=self.db.get_families(),
            request=self.request,
        ).qs
        return self.get_paginated_response(
            filtered_families, FamilyListSerializer, context=self.context
        )

    def create_family(self, *args, **kwargs):
        serializer = FamilyWriteSerializer(data=self.request.data, context=self.context)
        serializer.is_valid(raise_exception=True)
        family = serializer.save()
        return self.get_response_object(
            self.db.get_family(family.id),
            FamilyDetailSerializer,
            context=self.context,
            status_code=status.HTTP_201_CREATED,
        )

    def get_family(self, *args, **kwargs):
        return self.get_response_object(
            self.db.get_family(kwargs.get("id")),
            FamilyDetailSerializer,
            context=self.context,
        )

    def update_family(self, *args, **kwargs):
        family = self.db.get_family(kwargs.get("id"))
        serializer = FamilyWriteSerializer(
            family, data=self.request.data, partial=True, context=self.context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_response_object(
            self.db.get_family(family.id),
            FamilyDetailSerializer,
            context=self.context,
        )

    def delete_family(self, *args, **kwargs):
        # The variants stay as ordinary products.
        self.db.get_family(kwargs.get("id")).delete()
        return self.get_response_object(
            context=self.context, status_code=status.HTTP_204_NO_CONTENT
        )

    def create_variants(self, *args, **kwargs):
        family = self.db.get_family(kwargs.get("id"))
        serializer = VariantBulkCreateSerializer(
            data=self.request.data, context=self.context
        )
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["base_product"].family_id != family.id:
            raise field_error(
                "base_product",
                "base_product_not_in_family",
                "The base product must belong to the family.",
            )
        serializer.create_variants(family)
        return self.get_response_object(
            self.db.get_family(family.id),
            FamilyDetailSerializer,
            context=self.context,
            status_code=status.HTTP_201_CREATED,
        )
