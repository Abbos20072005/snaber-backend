from django.db.models.signals import pre_delete
from django.dispatch import receiver

from apps.product.models import AttributeValue, Product


@receiver(pre_delete, sender=Product)
def delete_product_variants_and_attributes(sender, instance, **kwargs):
    AttributeValue.objects.filter(
        productattributevalue__product__product=instance
    ).delete()
