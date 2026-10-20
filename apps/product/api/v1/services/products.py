from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.filters.products import ProductDynamicFilter, ProductFilter
from apps.product.api.v1.repositories.products import ProductRepository
from apps.product.api.v1.serializers.products import (
    GlobalSearchSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductImageUploadSerializer,
    ProductListSerializer,
)


class ProductService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ProductRepository()

    def get_products(self, *args, **kwargs):
        filtered_products = ProductFilter(
            data=self.request.query_params,
            queryset=self.db.get_products(only_active=False),
            request=self.request,
        ).qs
        return self.get_paginated_response(
            filtered_products, ProductListSerializer, context={"request": self.request}
        )

    def create_product(self, *args, **kwargs):
        serializer = ProductCreateUpdateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return self.get_response_object(
            self.db.get_product(product.id, only_active=False),
            ProductDetailSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def get_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"), only_active=False)
        return self.get_response_object(
            product, ProductDetailSerializer, context={"request": self.request}
        )

    def get_public_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"))
        return self.get_response_object(
            product, ProductDetailSerializer, context={"request": self.request}
        )

    def update_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"), only_active=False)
        serializer = ProductCreateUpdateSerializer(
            product,
            data=self.request.data,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.get_response_object(
            self.db.get_product(product.id, only_active=False),
            ProductDetailSerializer,
            context={"request": self.request},
        )

    def delete_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"), only_active=False)
        product.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def upload_images(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"), only_active=False)
        serializer = ProductImageUploadSerializer(
            data={"files": self.request.FILES.getlist("files")}
        )
        serializer.is_valid(raise_exception=True)
        images = self.db.add_images(product, serializer.validated_data["files"])
        return self.get_response(
            images,
            ProductImageSerializer,
            context={"request": self.request},
            many=True,
            status_code=status.HTTP_201_CREATED,
        )

    def delete_image(self, *args, **kwargs):
        image = self.db.get_image(kwargs.get("id"), kwargs.get("image_id"))
        image.file.delete(save=False)
        image.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def top_products(self, *args, **kwargs):
        filtered_products = ProductDynamicFilter(
            data=self.request.query_params,
            queryset=self.db.get_products(),
            request=self.request,
        ).qs
        return self.get_paginated_response(
            filtered_products, ProductListSerializer, context={"request": self.request}
        )

    def global_search(self, *args, **kwargs):
        items = self.db.get_all_items(self.request.query_params.get("search"))
        return self.get_response_object(
            items,
            GlobalSearchSerializer,
            context={"request": self.request},
        )
