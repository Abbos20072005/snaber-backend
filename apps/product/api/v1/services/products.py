from rest_framework import status

from apps.authentication.models import User
from apps.company.models import CompanyMember
from apps.core.exceptions import ObjectNotFoundException
from apps.core.services import BaseService, ViewService
from apps.product.api.v1.filters.products import ProductDynamicFilter, ProductFilter
from apps.product.api.v1.repositories.products import ProductRepository
from apps.product.api.v1.serializers.products import (
    GlobalSearchSerializer,
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class ProductService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = ProductRepository()

    def get_products(self, *args, **kwargs):
        user = self.request.user
        if user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            unfiltered_products = self.db.get_products()
        else:
            membership = (
                CompanyMember.objects.select_related("company")
                .filter(user=user)
                .first()
            )
            if not membership:
                return self.get_paginated_response(
                    [], context={"request": self.request}
                )
            unfiltered_products = self.db.get_products(membership.company)

        filtered_products = ProductFilter(
            data=self.request.query_params,
            queryset=unfiltered_products,
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

        user = self.request.user
        owner = serializer.validated_data.pop("owner", None)

        if user.role in (User.Roles.ADMIN, User.Roles.SUPER_ADMIN):
            if not owner:
                raise ObjectNotFoundException(message="Owner company is required")
        else:
            membership = (
                CompanyMember.objects.select_related("company")
                .filter(user=user)
                .first()
            )
            # Company feature is disabled for the frontend:
            # product can be created without a company
            owner = membership.company if membership else None

        product = serializer.save(owner=owner, creator=self.request.user)
        return self.get_response_object(
            product, ProductListSerializer, context={"request": self.request}
        )

    def get_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"))
        ViewService().register_view(self.request, product)
        return self.get_response_object(
            product, ProductDetailSerializer, context={"request": self.request}
        )

    def delete_product(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"))
        product.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )

    def update_product(self, *args, **kwargs):
        from apps.product.api.v1.services.constructors import ConstructorService

        return ConstructorService(request=self.request).update_product_via_constructor(
            *args, **kwargs
        )

    def top_products(self, *args, **kwargs):
        unfiltered_products = self.db.get_products()
        filtered_product = ProductDynamicFilter(
            data=self.request.query_params,
            queryset=unfiltered_products,
            request=self.request,
        ).qs
        return self.get_paginated_response(
            filtered_product, ProductListSerializer, context={"request": self.request}
        )

    def get_public_product_detail(self, *args, **kwargs):
        product = self.db.get_product(product_id=kwargs.get("id"))
        ViewService().register_view(self.request, product)
        return self.get_response_object(
            product, ProductDetailSerializer, context={"request": self.request}
        )

    def global_search(self, *args, **kwargs):
        search = self.request.query_params.get("search")
        items = self.db.get_all_items(search)
        return self.get_response_object(
            items,
            GlobalSearchSerializer,
            context={"request": self.request},
        )
