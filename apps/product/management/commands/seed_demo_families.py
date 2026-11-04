from django.core.management.base import BaseCommand
from django.db import transaction

from apps.product.models import (
    Attribute,
    AttributeValue,
    Category,
    Product,
    ProductAttributeValue,
    ProductFamily,
)

# Same tiers as seed_demo_products: the two demo products of a category are variants
# of one product that differ by grade.
GRADE_LABEL = ("Sinf", "Класс", "Grade")
TIERS = [
    ("Standart", "Стандарт", "Standard"),
    ("Professional", "Профессиональный", "Professional"),
]


class Command(BaseCommand):
    help = (
        "Group the demo products of every leaf category into one product family with "
        "a 'Grade' axis. Safe to run again: products already in a family are skipped."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        for category in Category.objects.filter(is_leaf=True).order_by("id"):
            products = [
                Product.objects.filter(
                    category=category, sku=f"SNB-{category.id}-{index + 1}"
                ).first()
                for index in range(len(TIERS))
            ]
            if not all(products) or any(product.family_id for product in products):
                continue

            axis, _ = Attribute.objects.get_or_create(
                category=category,
                name_en=GRADE_LABEL[2],
                defaults={
                    "name": GRADE_LABEL[2],
                    "name_uz": GRADE_LABEL[0],
                    "name_ru": GRADE_LABEL[1],
                    "attribute_type": Attribute.Type.SELECT,
                    "is_filterable": True,
                },
            )
            family = ProductFamily.objects.create(
                name=category.name_en,
                name_uz=category.name_uz,
                name_ru=category.name_ru,
                name_en=category.name_en,
                category=category,
            )
            family.axes.add(axis)

            for product, (tier_uz, tier_ru, tier_en) in zip(
                products, TIERS, strict=True
            ):
                value, _ = AttributeValue.objects.get_or_create(
                    attribute=axis,
                    value_en=tier_en,
                    defaults={
                        "value": tier_en,
                        "value_uz": tier_uz,
                        "value_ru": tier_ru,
                    },
                )
                ProductAttributeValue.objects.get_or_create(
                    product=product, attribute=axis, attribute_value=value
                )
                product.family = family
                product.save(update_fields=["family"])
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} product families."))
