from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Category


class CategoryRepository:
    def get_public_categories(self):
        categories = Category.objects.filter(is_active=True, parent__isnull=True)
        return categories

    def get_categories(self):
        categories = Category.objects.filter(parent__isnull=True)
        return categories

    def get_category(self, category_id):
        category = Category.objects.filter(id=category_id).first()
        if not category:
            raise ObjectNotFoundException(
                message="Category not found", message_key="category_not_found"
            )
        return category

    def get_public_category(self, category_id):
        category = Category.objects.filter(id=category_id, is_active=True).first()
        if not category:
            raise ObjectNotFoundException(
                message="Category not found", message_key="category_not_found"
            )
        return category
