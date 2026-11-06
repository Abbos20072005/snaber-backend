from django.core.management.base import BaseCommand

from apps.core.utils import optimize_image
from apps.product.signals.images import IMAGE_FIELDS

# Pictures smaller than this are already fine for the web.
MIN_SIZE = 300 * 1024


class Command(BaseCommand):
    help = (
        "Shrink the stored category, product and attribute value pictures that are "
        "bigger than 300 KB. Safe to run again: small pictures are skipped."
    )

    def handle(self, *args, **options):
        for model, field in IMAGE_FIELDS.items():
            for instance in model.objects.exclude(**{field: ""}).exclude(
                **{f"{field}__isnull": True}
            ):
                field_file = getattr(instance, field)
                if not field_file.storage.exists(field_file.name):
                    continue
                if field_file.size < MIN_SIZE:
                    continue

                old_name, old_size = field_file.name, field_file.size
                optimize_image(field_file)
                instance.save(update_fields=[field])
                if field_file.name != old_name:
                    field_file.storage.delete(old_name)
                self.stdout.write(
                    f"{old_name}: {old_size // 1024} KB -> {field_file.size // 1024} KB"
                )
