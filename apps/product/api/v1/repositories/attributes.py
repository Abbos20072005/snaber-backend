from django.db.models import Max, Min

from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Attribute, Category, Product


class AttributeRepository:
    def _get_category_ids(self, category_id):
        ids = []
        queue = [category_id]
        while queue:
            ids.extend(queue)
            queue = list(
                Category.objects.filter(parent_id__in=queue).values_list(
                    "id", flat=True
                )
            )
        return ids

    def get_attributes(self):
        attribute = (
            Attribute.objects.select_related("category", "category__parent")
            .prefetch_related("attribute_values")
            .all()
        )
        return attribute

    def get_attribute(self, attribute_id):
        attribute = Attribute.objects.filter(id=attribute_id).first()
        if not attribute:
            raise ObjectNotFoundException(
                message="Attribute not found",
                message_key="attribute_not_found",
            )
        return attribute

    def get_filterable_attributes(self, category_id=None):
        if not category_id:
            return Attribute.objects.none()
        return Attribute.objects.filter(
            is_filterable=True, category_id=category_id
        )

    def get_price_range(self, category_id=None):
        qs = Product.objects.filter(is_active=True)
        if category_id:
            descendant_ids = self._get_category_ids(category_id)
            qs = qs.filter(category_id__in=descendant_ids)
        result = qs.aggregate(min_price=Min("price_min"), max_price=Max("price_min"))
        return result.get("min_price") or 0, result.get("max_price") or 0
