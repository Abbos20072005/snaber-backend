from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.product.models import ProductAttributeValue, Variant


@receiver(pre_delete, sender=Variant)
def delete_attribute_values_of_variant(sender, instance, **kwargs):
    ProductAttributeValue.objects.filter(product=instance).values_list(
        "attribute_value_id", flat=True
    )
