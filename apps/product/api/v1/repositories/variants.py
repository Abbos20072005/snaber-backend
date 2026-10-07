from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Variant, VariantConstructor


class ProductVariantRepository:
    def get_variant(self, variant_id):
        variant = Variant.objects.filter(id=variant_id).first()
        if not variant:
            raise ObjectNotFoundException(
                message="Product variant not found",
                message_key="product_variant_not_found",
            )

        return variant

    def get_constructor(self, constructor_id):
        variant = VariantConstructor.objects.filter(id=constructor_id).first()
        if not variant:
            raise ObjectNotFoundException(
                message="Product variant not found",
                message_key="product_variant_not_found",
            )

        return variant

    def delete_variant_constructor(self, constructor_id):
        variant = VariantConstructor.objects.filter(id=constructor_id).first()
        if not variant:
            raise ObjectNotFoundException(
                message="Variant constructor not found",
                message_key="variant_constructor_not_found",
            )
        variant.delete()
        return variant
