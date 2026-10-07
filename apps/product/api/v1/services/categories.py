from rest_framework import status

from apps.core.services import BaseService
from apps.product.api.v1.filters.catigories import CategoryFilter
from apps.product.api.v1.repositories.categories import CategoryRepository
from apps.product.api.v1.serializers.categories import (
    CategoriesListSerializer,
    CategoryBreadcrumbHelperSerializer,
    CategoryCreateSerializer,
    CategoryListSerializer,
    CategoryUpdateSerializer,
)


class CategoryService(BaseService):
    def __init__(self, request):
        super().__init__(request)
        self.db = CategoryRepository()

    def get_public_child_categories(self, *args, **kwargs):
        category_id = kwargs.get("id")
        categories = self.db.get_public_category(category_id)

        return self.get_response_object(
            categories, CategoriesListSerializer, context={"request": self.request}
        )

    def get_public_categories(self, *args, **kwargs):
        categories = self.db.get_public_categories()
        filtered_categories = CategoryFilter(
            data=self.request.query_params,
            queryset=categories,
            request=self.request,
        ).qs
        return self.get_response(
            filtered_categories,
            CategoryListSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_categories(self, *args, **kwargs):
        categories = self.db.get_categories()
        return self.get_response(
            categories,
            CategoryListSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_child_categories(self, *args, **kwargs):
        category_id = kwargs.get("id")
        child_categories = self.db.get_category(category_id)
        return self.get_response_object(
            child_categories,
            CategoriesListSerializer,
            context={"request": self.request},
        )

    def create_category(self, *args, **kwargs):
        serializer = CategoryCreateSerializer(
            data=self.request.data, context={"request": self.request}
        )
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return self.get_response_object(
            category,
            CategoryListSerializer,
            context={"request": self.request},
            status_code=status.HTTP_201_CREATED,
        )

    def get_category_breadcrumbs(self, *args, **kwargs):
        category_id = kwargs.get("id")
        category = self.db.get_category(category_id)
        breadcrumbs = category.get_breadcrumbs()
        return self.get_response(
            breadcrumbs,
            CategoryBreadcrumbHelperSerializer,
            many=True,
            context={"request": self.request},
        )

    def get_public_category_breadcrumbs(self, *args, **kwargs):
        category_id = kwargs.get("id")
        category = self.db.get_public_category(category_id)
        breadcrumbs = category.get_breadcrumbs()
        return self.get_response(
            breadcrumbs,
            CategoryBreadcrumbHelperSerializer,
            many=True,
            context={"request": self.request},
        )

    def update_category(self, *args, **kwargs):
        category_id = kwargs.get("id")
        old_category = self.db.get_category(category_id)
        serializer = CategoryUpdateSerializer(
            data=self.request.data,
            instance=old_category,
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid(raise_exception=True)
        new_category = serializer.save()
        return self.get_response_object(
            new_category, CategoryListSerializer, context={"request": self.request}
        )

    def delete_category(self, *args, **kwargs):
        category_id = kwargs.get("id")
        old_category = self.db.get_category(category_id)
        old_category.delete()
        return self.get_response_object(
            context={"request": self.request}, status_code=status.HTTP_204_NO_CONTENT
        )
