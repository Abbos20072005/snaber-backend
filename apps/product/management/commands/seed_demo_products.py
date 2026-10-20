import os
import random
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.product.models import (
    Category,
    Product,
    ProductCharacteristic,
    ProductImage,
    Unit,
)

IMAGE_DIR = "products/catalog"

# (uz, ru, en) tier labels; every leaf category gets one product per tier.
TIERS = [
    ("Standart", "Стандарт", "Standard"),
    ("Professional", "Профессиональный", "Professional"),
]
TYPE_LABEL = ("Turi", "Тип", "Type")


class Command(BaseCommand):
    help = (
        "Replace all products with demo products (two per leaf category) using "
        "images from media/products/catalog/<category_id>.jpg. Edit them in the admin."
    )

    def add_arguments(self, parser):
        parser.add_argument("--confirm", action="store_true")

    def handle(self, *args, **options):
        if not options["confirm"]:
            raise CommandError("This deletes all products. Re-run with --confirm.")

        unit = Unit.objects.filter(unit_en="pcs").first() or Unit.objects.first()
        leaves = list(Category.objects.filter(is_leaf=True).order_by("id"))
        missing = [
            c.id
            for c in leaves
            if not os.path.exists(
                os.path.join(settings.MEDIA_ROOT, IMAGE_DIR, f"{c.id}.jpg")
            )
        ]
        if missing:
            raise CommandError(f"Missing images for categories: {missing}")

        with transaction.atomic():
            Product.objects.all().delete()
            created = 0
            for category in leaves:
                rng = random.Random(category.id)
                base_price = rng.randrange(15, 900) * 1000
                for index, (tier_uz, tier_ru, tier_en) in enumerate(TIERS):
                    price = Decimal(base_price * (1 + index * 0.6) // 1000 * 1000)
                    name = {
                        "uz": f"{category.name_uz} — {tier_uz}",
                        "ru": f"{category.name_ru} — {tier_ru}",
                        "en": f"{category.name_en} — {tier_en}",
                    }
                    description = {
                        "uz": f"{category.name_uz}: {tier_uz.lower()} sinf, ishonchli sifat.",
                        "ru": f"{category.name_ru}: класс «{tier_ru.lower()}», надёжное качество.",
                        "en": f"{category.name_en}: {tier_en.lower()} grade, reliable quality.",
                    }
                    product = Product.objects.create(
                        name=name["en"],
                        name_uz=name["uz"],
                        name_ru=name["ru"],
                        name_en=name["en"],
                        description=description["en"],
                        description_uz=description["uz"],
                        description_ru=description["ru"],
                        description_en=description["en"],
                        category=category,
                        sku=f"SNB-{category.id}-{index + 1}",
                        unit=unit,
                        price=price,
                        discount_percent=10 if rng.random() < 0.3 else 0,
                        stock_quantity=rng.randrange(5, 200),
                        is_active=True,
                    )
                    ProductImage.objects.create(
                        product=product, file=f"{IMAGE_DIR}/{category.id}.jpg"
                    )
                    ProductCharacteristic.objects.create(
                        product=product,
                        name=TYPE_LABEL[2],
                        name_uz=TYPE_LABEL[0],
                        name_ru=TYPE_LABEL[1],
                        name_en=TYPE_LABEL[2],
                        value=tier_en,
                        value_uz=tier_uz,
                        value_ru=tier_ru,
                        value_en=tier_en,
                    )
                    created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} products in {len(leaves)} categories.")
        )
