from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import AttributeValue


class AttributeValueRepository:
    def get_values(self):
        return AttributeValue.objects.select_related(
            "attribute", "attribute__category", "attribute__category__parent"
        ).all()

    def get_value(self, value_id):
        value = AttributeValue.objects.filter(id=value_id).first()
        if not value:
            raise ObjectNotFoundException(
                message="Attribute value not found",
                message_key="attribute_value_not_found",
            )
        return value
