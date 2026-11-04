from django.db.models import Count, Prefetch

from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Product, ProductFamily


class FamilyRepository:
    def get_families(self):
        return ProductFamily.objects.annotate(variants_count=Count("variants"))

    def get_family(self, family_id):
        family = (
            ProductFamily.objects.prefetch_related(
                "axes__attribute_values",
                Prefetch(
                    "variants",
                    queryset=Product.objects.select_related("unit").prefetch_related(
                        "images", "product_attribute_values__attribute_value"
                    ),
                ),
            )
            .filter(id=family_id)
            .first()
        )
        if not family:
            raise ObjectNotFoundException(
                message="Product family not found",
                message_key="product_family_not_found",
            )
        return family
