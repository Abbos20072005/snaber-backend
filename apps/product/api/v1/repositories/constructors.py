from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import ProductConstructor


class ConstructorRepository:
    def get_product_constructors(self, company=None):
        if company:
            return ProductConstructor.objects.filter(owner=company)
        return ProductConstructor.objects.all()

    def get_pending_constructors(self, company=None):
        if not company:
            return ProductConstructor.objects.exclude(
                status=ProductConstructor.Status.ACCEPTED
            )
        return ProductConstructor.objects.exclude(
            status=ProductConstructor.Status.ACCEPTED
        ).filter(owner=company)

    def get_product_constructor(self, constructor_id):
        constructor = (
            ProductConstructor.objects.select_related("owner", "category", "moq_unit")
            .prefetch_related(
                "owner__industries",
                "variant_constructors__attribute_value_constructors__attribute",
                "variant_constructors__attribute_value_constructors__attribute_value",
                "variant_constructors__variant_media_constructors",
                "variant_constructors__characteristic_constructors",
            )
            .filter(id=constructor_id)
            .first()
        )
        if not constructor:
            raise ObjectNotFoundException(
                message="Product constructor not found",
                message_key="product_constructor_not_found",
            )
        return constructor

    def delete_product_constructor(self, constructor_id):
        constructor = ProductConstructor.objects.filter(id=constructor_id).first()
        if not constructor:
            raise ObjectNotFoundException(
                message="Product constructor not found",
                message_key="product_constructor_not_found",
            )
        constructor.delete()
        return constructor
