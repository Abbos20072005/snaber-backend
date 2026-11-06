from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.core.utils import optimize_image
from apps.product.models import AttributeValue, Category, ProductImage

IMAGE_FIELDS = {
    AttributeValue: "image",
    Category: "image",
    ProductImage: "file",
}


@receiver(pre_save, sender=AttributeValue)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=ProductImage)
def optimize_uploaded_image(sender, instance, **kwargs):
    field_file = getattr(instance, IMAGE_FIELDS[sender])
    # Only a freshly uploaded file is shrunk, files already in the storage are kept.
    if field_file and not field_file._committed:
        optimize_image(field_file)
