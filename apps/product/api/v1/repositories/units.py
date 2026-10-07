from apps.core.exceptions import ObjectNotFoundException
from apps.product.models import Unit


class UnitRepository:
    def get_units(self):
        return Unit.objects.all()

    def get_unit(self, unit_id):
        unit = Unit.objects.filter(id=unit_id).first()
        if not unit:
            raise ObjectNotFoundException(
                message="Unit not found",
                message_key="unit_not_found",
            )
        return unit
