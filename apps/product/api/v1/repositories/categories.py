from django.db.models import Count

from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Category, Product


class CategoryRepository:
    def get_public_categories(self):
        categories = Category.objects.filter(
            is_active=True, parent__isnull=True
        ).prefetch_related("children", "children__children")
        return categories

    def get_products_counts(self):
        # Active products per category, rolled up through all active subcategories.
        direct = (
            Product.objects.filter(is_active=True)
            .order_by()
            .values("category_id")
            .annotate(total=Count("id"))
        )
        counts = {item["category_id"]: item["total"] for item in direct}
        parents = dict(
            Category.objects.filter(is_active=True).values_list("id", "parent_id")
        )
        totals = {}
        for category_id, total in counts.items():
            while category_id in parents:
                totals[category_id] = totals.get(category_id, 0) + total
                category_id = parents[category_id]
        return totals

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
