"""Add extra building-materials categories without wiping existing data.

Adds 6 root categories (12 leafs, 24 products) for the home grid.
Photos must exist in media/seed/<leaf-code>.jpg (see /tmp/fetch_extra_images.py).

Usage:
    python manage.py seed_extra_categories --confirm
"""

import os
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

MEDIA_SEED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "media", "seed")

ROOTS_EXTRA = [
    {
        "code": "doors-windows",
        "n": ("Doors & Windows", "Двери и окна", "Eshik va derazalar"),
        "children": [
            {
                "code": "interior-doors",
                "n": ("Interior Doors", "Межкомнатные двери", "Xona eshiklari"),
                "attrs": [
                    (("Brand", "Бренд", "Brend"), ["Belwood", "Profil Doors"]),
                    (
                        ("Color", "Цвет", "Rang"),
                        [("White", "Белый", "Oq"), ("Wenge", "Венге", "Venge")],
                    ),
                    (("Size", "Размер", "O'lcham"), ["600x2000", "800x2000"]),
                ],
                "products": [
                    {
                        "n": (
                            "MDF interior door, white 800x2000",
                            "Дверь МДФ белая 800x2000",
                            "MDF xona eshigi, oq 800x2000",
                        ),
                        "moq": 2, "unit": "pcs", "lead": (3, 10),
                        "variants": [
                            {"v": {"Brand": "Belwood", "Color": "White", "Size": "800x2000"}, "price": 1850000, "stock": 60},
                            {"v": {"Brand": "Belwood", "Color": "White", "Size": "600x2000"}, "price": 1750000, "stock": 40},
                        ],
                        "chars": [("Material", "MDF"), ("Coating", "PVC film"), ("Warranty", "2 years")],
                    },
                    {
                        "n": (
                            "MDF interior door, wenge 600x2000",
                            "Дверь МДФ венге 600x2000",
                            "MDF xona eshigi, venge 600x2000",
                        ),
                        "moq": 2, "unit": "pcs", "lead": (3, 10),
                        "variants": [
                            {"v": {"Brand": "Profil Doors", "Color": "Wenge", "Size": "600x2000"}, "price": 1950000, "stock": 50},
                        ],
                        "chars": [("Material", "MDF"), ("Coating", "Eco-veneer"), ("Warranty", "2 years")],
                    },
                ],
            },
            {
                "code": "pvc-windows",
                "n": ("PVC Windows", "Пластиковые окна", "Plastik derazalar"),
                "attrs": [
                    (("Chambers", "Камеры", "Kameralar"), ["3", "5"]),
                    (
                        ("Opening", "Открывание", "Ochilish"),
                        [("Fixed", "Глухое", "Kar"), ("Tilt-turn", "Поворотно-откидное", "Burilishli")],
                    ),
                ],
                "products": [
                    {
                        "n": ("PVC window 3-chamber, tilt-turn", "Окно ПВХ 3-камерное, поворотно-откидное", "PVX deraza 3-kamerali, burilishli"),
                        "moq": 2, "unit": "pcs", "lead": (5, 12),
                        "variants": [
                            {"v": {"Chambers": "3", "Opening": "Tilt-turn"}, "price": 1450000, "stock": 80},
                            {"v": {"Chambers": "3", "Opening": "Fixed"}, "price": 1100000, "stock": 60},
                        ],
                        "chars": [("Profile", "60 mm"), ("Glass", "Double-glazed"), ("Warranty", "5 years")],
                    },
                    {
                        "n": ("PVC window 5-chamber, tilt-turn", "Окно ПВХ 5-камерное, поворотно-откидное", "PVX deraza 5-kamerali, burilishli"),
                        "moq": 2, "unit": "pcs", "lead": (5, 12),
                        "variants": [
                            {"v": {"Chambers": "5", "Opening": "Tilt-turn"}, "price": 1950000, "stock": 50},
                        ],
                        "chars": [("Profile", "70 mm"), ("Glass", "Double-glazed energy-saving"), ("Warranty", "5 years")],
                    },
                ],
            },
        ],
    },
    {
        "code": "heating",
        "n": ("Heating", "Отопление", "Isitish"),
        "children": [
            {
                "code": "radiators",
                "n": ("Radiators", "Радиаторы", "Radiatorlar"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [("Bimetallic", "Биметаллический", "Bimetall"), ("Aluminum", "Алюминиевый", "Alyumin")],
                    ),
                    (("Sections", "Секции", "Seksiyalar"), ["6", "8", "10"]),
                ],
                "products": [
                    {
                        "n": ("Bimetallic radiator, 10 sections", "Радиатор биметаллический, 10 секций", "Bimetall radiator, 10 seksiya"),
                        "moq": 4, "unit": "pcs", "lead": (2, 6),
                        "variants": [
                            {"v": {"Type": "Bimetallic", "Sections": "10"}, "price": 850000, "stock": 300},
                            {"v": {"Type": "Bimetallic", "Sections": "8"}, "price": 700000, "stock": 250},
                        ],
                        "chars": [("Heat output", "180 W/section"), ("Pressure", "16 bar"), ("Warranty", "10 years")],
                    },
                    {
                        "n": ("Aluminum radiator, 8 sections", "Радиатор алюминиевый, 8 секций", "Alyumin radiator, 8 seksiya"),
                        "moq": 4, "unit": "pcs", "lead": (2, 6),
                        "variants": [
                            {"v": {"Type": "Aluminum", "Sections": "8"}, "price": 620000, "stock": 280},
                        ],
                        "chars": [("Heat output", "190 W/section"), ("Pressure", "12 bar"), ("Warranty", "10 years")],
                    },
                ],
            },
            {
                "code": "heated-floors",
                "n": ("Heated Floors", "Тёплые полы", "Issiq pollar"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [("Cable", "Кабель", "Kabel"), ("Mat", "Мат", "Mat")],
                    ),
                    (("Area", "Площадь", "Maydon"), ["2 m2", "4 m2", "6 m2"]),
                ],
                "products": [
                    {
                        "n": ("Heating cable, 4 m2", "Нагревательный кабель, 4 м2", "Isituvchi kabel, 4 m2"),
                        "moq": 2, "unit": "set", "lead": (2, 5),
                        "variants": [
                            {"v": {"Type": "Cable", "Area": "4 m2"}, "price": 950000, "stock": 120},
                            {"v": {"Type": "Cable", "Area": "2 m2"}, "price": 550000, "stock": 100},
                        ],
                        "chars": [("Power", "150 W/m2"), ("Thermostat", "Included"), ("Warranty", "15 years")],
                    },
                    {
                        "n": ("Heating mat, 2 m2", "Нагревательный мат, 2 м2", "Isituvchi mat, 2 m2"),
                        "moq": 2, "unit": "set", "lead": (2, 5),
                        "variants": [
                            {"v": {"Type": "Mat", "Area": "2 m2"}, "price": 720000, "stock": 110},
                        ],
                        "chars": [("Power", "150 W/m2"), ("Thickness", "3 mm"), ("Warranty", "15 years")],
                    },
                ],
            },
        ],
    },
    {
        "code": "waterproofing",
        "n": ("Waterproofing", "Гидроизоляция", "Gidroizolyatsiya"),
        "children": [
            {
                "code": "membranes",
                "n": ("Membranes", "Мембраны", "Membranalar"),
                "attrs": [
                    (("Thickness", "Толщина", "Qalinlik"), ["1.2 mm", "1.5 mm", "2.0 mm"]),
                    (("Width", "Ширина", "Kenglik"), ["1 m", "2 m"]),
                ],
                "products": [
                    {
                        "n": ("PVC membrane 1.5 mm, 2 m", "ПВХ мембрана 1.5 мм, 2 м", "PVX membrana 1.5 mm, 2 m"),
                        "moq": 5, "unit": "roll", "lead": (2, 6),
                        "variants": [
                            {"v": {"Thickness": "1.5 mm", "Width": "2 m"}, "price": 145000, "stock": 400},
                            {"v": {"Thickness": "1.2 mm", "Width": "2 m"}, "price": 120000, "stock": 350},
                        ],
                        "chars": [("Use", "Roofs, foundations"), ("UV resistance", "Yes"), ("Roll", "20 m")],
                    },
                    {
                        "n": ("EPDM membrane 1.2 mm, 1 m", "ЭПДМ мембрана 1.2 мм, 1 м", "EPDM membrana 1.2 mm, 1 m"),
                        "moq": 5, "unit": "roll", "lead": (2, 6),
                        "variants": [
                            {"v": {"Thickness": "1.2 mm", "Width": "1 m"}, "price": 165000, "stock": 300},
                        ],
                        "chars": [("Use", "Roofs, ponds"), ("Elongation", "300%"), ("Roll", "15 m")],
                    },
                ],
            },
            {
                "code": "bitumen-mastic",
                "n": ("Bitumen Mastic", "Битумная мастика", "Bitum mastikasi"),
                "attrs": [
                    (("Weight", "Вес", "Og'irlik"), ["20 kg", "25 kg"]),
                ],
                "products": [
                    {
                        "n": ("Bitumen mastic, 20 kg", "Мастика битумная, 20 кг", "Bitum mastikasi, 20 kg"),
                        "moq": 10, "unit": "pcs", "lead": (1, 3),
                        "variants": [
                            {"v": {"Weight": "20 kg"}, "price": 320000, "stock": 600},
                        ],
                        "chars": [("Consumption", "1.5 kg/m2"), ("Drying", "24 hours"), ("Use", "Foundations, roofs")],
                    },
                    {
                        "n": ("Bitumen mastic, 25 kg", "Мастика битумная, 25 кг", "Bitum mastikasi, 25 kg"),
                        "moq": 10, "unit": "pcs", "lead": (1, 3),
                        "variants": [
                            {"v": {"Weight": "25 kg"}, "price": 390000, "stock": 500},
                        ],
                        "chars": [("Consumption", "2 kg/m2"), ("Drying", "24 hours"), ("Use", "Foundations, roofs")],
                    },
                ],
            },
        ],
    },
    {
        "code": "fasteners",
        "n": ("Fasteners", "Крепёж", "Mahkamlagichlar"),
        "children": [
            {
                "code": "anchors",
                "n": ("Anchors", "Анкеры", "Ankerlar"),
                "attrs": [
                    (("Size", "Размер", "O'lcham"), ["M8x60", "M10x80", "M12x100"]),
                    (("Pack", "Упаковка", "Qadoq"), ["50 pcs", "100 pcs"]),
                ],
                "products": [
                    {
                        "n": ("Wedge anchor M10x80, 100 pcs", "Анкер клиновой M10x80, 100 шт", "Pona anker M10x80, 100 dona"),
                        "moq": 5, "unit": "box", "lead": (1, 3),
                        "variants": [
                            {"v": {"Size": "M10x80", "Pack": "100 pcs"}, "price": 240000, "stock": 800},
                            {"v": {"Size": "M8x60", "Pack": "100 pcs"}, "price": 180000, "stock": 700},
                        ],
                        "chars": [("Material", "Zinc-plated steel"), ("Use", "Concrete, brick"), ("Standard", "ETA")],
                    },
                    {
                        "n": ("Wedge anchor M12x100, 50 pcs", "Анкер клиновой M12x100, 50 шт", "Pona anker M12x100, 50 dona"),
                        "moq": 5, "unit": "box", "lead": (1, 3),
                        "variants": [
                            {"v": {"Size": "M12x100", "Pack": "50 pcs"}, "price": 210000, "stock": 600},
                        ],
                        "chars": [("Material", "Zinc-plated steel"), ("Use", "Concrete"), ("Standard", "ETA")],
                    },
                ],
            },
            {
                "code": "screws",
                "n": ("Screws", "Саморезы", "Samorezlar"),
                "attrs": [
                    (("Size", "Размер", "O'lcham"), ["3.5x25", "3.5x45", "4.2x75"]),
                    (("Pack", "Упаковка", "Qadoq"), ["500 pcs", "1000 pcs"]),
                ],
                "products": [
                    {
                        "n": ("Self-tapping screw 3.5x45, 1000 pcs", "Саморез 3.5x45, 1000 шт", "Samorez 3.5x45, 1000 dona"),
                        "moq": 5, "unit": "box", "lead": (1, 3),
                        "variants": [
                            {"v": {"Size": "3.5x45", "Pack": "1000 pcs"}, "price": 195000, "stock": 1000},
                            {"v": {"Size": "3.5x25", "Pack": "1000 pcs"}, "price": 150000, "stock": 900},
                        ],
                        "chars": [("Material", "Phosphated steel"), ("Use", "Drywall, wood"), ("Head", "Countersunk")],
                    },
                    {
                        "n": ("Self-tapping screw 4.2x75, 500 pcs", "Саморез 4.2x75, 500 шт", "Samorez 4.2x75, 500 dona"),
                        "moq": 5, "unit": "box", "lead": (1, 3),
                        "variants": [
                            {"v": {"Size": "4.2x75", "Pack": "500 pcs"}, "price": 175000, "stock": 800},
                        ],
                        "chars": [("Material", "Zinc-plated steel"), ("Use", "Wood, metal"), ("Head", "Hex")],
                    },
                ],
            },
        ],
    },
    {
        "code": "welding",
        "n": ("Welding", "Сварка", "Payvandlash"),
        "children": [
            {
                "code": "electrodes",
                "n": ("Electrodes", "Электроды", "Elektrodlar"),
                "attrs": [
                    (("Diameter", "Диаметр", "Diametr"), ["3 mm", "4 mm"]),
                    (("Pack", "Упаковка", "Qadoq"), ["5 kg", "25 kg"]),
                ],
                "products": [
                    {
                        "n": ("Welding electrodes MP-3, 3 mm 5 kg", "Электроды МР-3, 3 мм 5 кг", "MP-3 elektrodlar, 3 mm 5 kg"),
                        "moq": 10, "unit": "pack", "lead": (1, 3),
                        "variants": [
                            {"v": {"Diameter": "3 mm", "Pack": "5 kg"}, "price": 145000, "stock": 900},
                        ],
                        "chars": [("Coating", "Rutile"), ("Current", "AC/DC"), ("Standard", "GOST 9466")],
                    },
                    {
                        "n": ("Welding electrodes MP-3, 4 mm 5 kg", "Электроды МР-3, 4 мм 5 кг", "MP-3 elektrodlar, 4 mm 5 kg"),
                        "moq": 10, "unit": "pack", "lead": (1, 3),
                        "variants": [
                            {"v": {"Diameter": "4 mm", "Pack": "5 kg"}, "price": 140000, "stock": 800},
                            {"v": {"Diameter": "4 mm", "Pack": "25 kg"}, "price": 650000, "stock": 300},
                        ],
                        "chars": [("Coating", "Rutile"), ("Current", "AC/DC"), ("Standard", "GOST 9466")],
                    },
                ],
            },
            {
                "code": "inverters",
                "n": ("Welding Inverters", "Сварочные инверторы", "Payvandlash invertorlari"),
                "attrs": [
                    (("Current", "Ток", "Tok"), ["160 A", "200 A", "250 A"]),
                ],
                "products": [
                    {
                        "n": ("Welding inverter 200 A", "Сварочный инвертор 200 А", "Payvandlash invertori 200 A"),
                        "moq": 2, "unit": "pcs", "lead": (2, 6),
                        "variants": [
                            {"v": {"Current": "200 A"}, "price": 1850000, "stock": 90},
                        ],
                        "chars": [("Power", "5.4 kW"), ("Duty cycle", "60%"), ("Warranty", "2 years")],
                    },
                    {
                        "n": ("Welding inverter 160 A", "Сварочный инвертор 160 А", "Payvandlash invertori 160 A"),
                        "moq": 2, "unit": "pcs", "lead": (2, 6),
                        "variants": [
                            {"v": {"Current": "160 A"}, "price": 1500000, "stock": 100},
                        ],
                        "chars": [("Power", "4 kW"), ("Duty cycle", "60%"), ("Warranty", "2 years")],
                    },
                ],
            },
        ],
    },
    {
        "code": "ladders-scaffolding",
        "n": ("Ladders", "Лестницы", "Narvonlar"),
        "children": [
            {
                "code": "step-ladders",
                "n": ("Step Ladders", "Стремянки", "Narvonlar"),
                "attrs": [
                    (("Steps", "Ступени", "Pog'onalar"), ["4", "5", "6", "8"]),
                    (
                        ("Material", "Материал", "Material"),
                        [("Aluminum", "Алюминий", "Alyumin")],
                    ),
                ],
                "products": [
                    {
                        "n": ("Aluminum step ladder, 5 steps", "Стремянка алюминиевая, 5 ступеней", "Alyumin narvon, 5 pog'ona"),
                        "moq": 2, "unit": "pcs", "lead": (2, 5),
                        "variants": [
                            {"v": {"Steps": "5", "Material": "Aluminum"}, "price": 850000, "stock": 150},
                            {"v": {"Steps": "6", "Material": "Aluminum"}, "price": 980000, "stock": 120},
                        ],
                        "chars": [("Load", "150 kg"), ("Height", "1.6 m"), ("Standard", "EN 131")],
                    },
                    {
                        "n": ("Aluminum step ladder, 8 steps", "Стремянка алюминиевая, 8 ступеней", "Alyumin narvon, 8 pog'ona"),
                        "moq": 2, "unit": "pcs", "lead": (2, 5),
                        "variants": [
                            {"v": {"Steps": "8", "Material": "Aluminum"}, "price": 1350000, "stock": 90},
                        ],
                        "chars": [("Load", "150 kg"), ("Height", "2.5 m"), ("Standard", "EN 131")],
                    },
                ],
            },
            {
                "code": "extension-ladders",
                "n": ("Extension Ladders", "Приставные лестницы", "Tirama narvonlar"),
                "attrs": [
                    (("Length", "Длина", "Uzunlik"), ["3 m", "4 m", "6 m"]),
                    (("Sections", "Секции", "Seksiyalar"), ["2", "3"]),
                ],
                "products": [
                    {
                        "n": ("Extension ladder 2-section, 6 m", "Лестница 2-секционная, 6 м", "2-seksiyali narvon, 6 m"),
                        "moq": 2, "unit": "pcs", "lead": (2, 5),
                        "variants": [
                            {"v": {"Length": "6 m", "Sections": "2"}, "price": 1250000, "stock": 100},
                        ],
                        "chars": [("Load", "150 kg"), ("Material", "Aluminum"), ("Standard", "EN 131")],
                    },
                    {
                        "n": ("Extension ladder 3-section, 6 m", "Лестница 3-секционная, 6 м", "3-seksiyali narvon, 6 m"),
                        "moq": 2, "unit": "pcs", "lead": (2, 5),
                        "variants": [
                            {"v": {"Length": "6 m", "Sections": "3"}, "price": 1550000, "stock": 80},
                        ],
                        "chars": [("Load", "150 kg"), ("Material", "Aluminum"), ("Standard", "EN 131")],
                    },
                ],
            },
        ],
    },
]

EXTRA_UNITS = [
    ("pack", "пачка", "pachka"),
]


def _t(value):
    if isinstance(value, (list, tuple)):
        en, ru, uz = value
        return en, ru, uz
    return value, value, value


class Command(BaseCommand):
    help = "Add extra building-materials categories without wiping data."

    def add_arguments(self, parser):
        parser.add_argument("--confirm", action="store_true")

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(self.style.WARNING("Run with --confirm"))
            return

        from django.contrib.auth import get_user_model

        from apps.company.models import Company
        from apps.product.models import (
            Attribute,
            AttributeValue,
            Category,
            Characteristic,
            Product,
            ProductAttributeValue,
            Unit,
            Variant,
            VariantAttributeStock,
            VariantMedia,
        )

        existing = set(Category.objects.values_list("code", flat=True))
        todo = [r for r in ROOTS_EXTRA if r["code"] not in existing]
        if not todo:
            self.stdout.write(self.style.SUCCESS("Extra categories already seeded."))
            return

        with transaction.atomic():
            company = Company.objects.filter(status="active").first() or Company.objects.first()
            user = get_user_model().objects.order_by("id").first()

            unit_map = {u.unit: u for u in Unit.objects.all()}
            for en, ru, uz in EXTRA_UNITS:
                unit_map[en] = Unit.objects.create(unit=en, unit_ru=ru, unit_uz=uz)

            stats = {"roots": 0, "leafs": 0, "attrs": 0, "values": 0, "products": 0, "variants": 0}
            view_seed = 500

            for root in todo:
                root_en, root_ru, root_uz = root["n"]
                root_cat = Category.objects.create(
                    code=root["code"], name=root_en, name_en=root_en,
                    name_ru=root_ru, name_uz=root_uz, parent=None,
                    level=0, is_leaf=False, is_active=True,
                )
                stats["roots"] += 1

                for leaf in root["children"]:
                    leaf_en, leaf_ru, leaf_uz = leaf["n"]
                    photo = f"seed/{leaf['code']}.jpg"
                    photo_path = os.path.join(str(MEDIA_SEED_DIR), f"{leaf['code']}.jpg")
                    leaf_cat = Category.objects.create(
                        code=leaf["code"], name=leaf_en, name_en=leaf_en,
                        name_ru=leaf_ru, name_uz=leaf_uz, parent=root_cat,
                        level=1, is_leaf=True, is_active=True,
                        image=photo if os.path.exists(photo_path) else None,
                    )
                    stats["leafs"] += 1

                    attr_map = {}
                    for attr_names, values in leaf["attrs"]:
                        attr_en, attr_ru, attr_uz = attr_names
                        attr = Attribute.objects.create(
                            name=attr_en, name_en=attr_en, name_ru=attr_ru,
                            name_uz=attr_uz, attribute_type=Attribute.Type.SELECT,
                            category=leaf_cat, is_filterable=True,
                        )
                        stats["attrs"] += 1
                        value_map = {}
                        for entry in values:
                            val_en, val_ru, val_uz = _t(entry)
                            value_map[val_en] = AttributeValue.objects.create(
                                attribute=attr, value=val_en, value_en=val_en,
                                value_ru=val_ru, value_uz=val_uz,
                            )
                            stats["values"] += 1
                        attr_map[attr_en] = (attr, value_map)

                    for p_idx, product in enumerate(leaf["products"], start=1):
                        p_en, p_ru, p_uz = product["n"]
                        prices = [v["price"] for v in product["variants"]]
                        view_seed = (view_seed * 37 + 101) % 900
                        prod = Product.objects.create(
                            name=p_en, name_en=p_en, name_ru=p_ru, name_uz=p_uz,
                            creator=None, owner=company, category=leaf_cat,
                            sku=f"BM-{leaf['code']}-{p_idx:03d}".upper(),
                            image=photo if os.path.exists(photo_path) else None,
                            product_type=Product.ProductType.READY,
                            price_type=Product.PriceType.RANGE
                            if len(set(prices)) > 1 else Product.PriceType.EXACT,
                            price_min=Decimal(min(prices)), price_max=Decimal(max(prices)),
                            is_active=True, moq=product["moq"],
                            moq_unit=unit_map[product["unit"]],
                            lead_time_min=product["lead"][0], lead_time_max=product["lead"][1],
                            average_rating=Decimal("4.5"), view_count=100 + view_seed,
                        )
                        stats["products"] += 1

                        for v_idx, variant in enumerate(product["variants"], start=1):
                            var = Variant.objects.create(
                                product=prod,
                                description=f"{p_en} — option {v_idx}",
                                description_en=f"{p_en} — option {v_idx}",
                                description_ru=f"{p_ru} — вариант {v_idx}",
                                description_uz=f"{p_uz} — {v_idx}-variant",
                                sku_variant=f"{prod.sku}-V{v_idx}",
                                price_override=Decimal(variant["price"]),
                                moq_override=product["moq"],
                                stock_quantity=variant["stock"],
                                is_active=True, average_rating=Decimal("4.5"),
                            )
                            stats["variants"] += 1

                            linked = []
                            for attr_en, val_en in variant["v"].items():
                                attr, value_map = attr_map[attr_en]
                                attr_value = value_map[val_en]
                                ProductAttributeValue.objects.create(
                                    product=var, attribute=attr, attribute_value=attr_value,
                                )
                                linked.append(attr_value)

                            stock = VariantAttributeStock.objects.create(
                                variant=var, quantity=variant["stock"]
                            )
                            if linked:
                                stock.attribute_values.add(*linked)

                            for char_name, char_value in product.get("chars", []):
                                Characteristic.objects.create(
                                    product_variant=var, name=char_name, value=char_value,
                                )

                            if user is not None and os.path.exists(photo_path):
                                VariantMedia.objects.create(
                                    user=user, product_variant=var, file=photo,
                                    product_media_type=VariantMedia.MediaType.PHOTO,
                                )

            # Roots reuse their first child's photo.
            for root in todo:
                root_cat = Category.objects.get(code=root["code"])
                first_child = root_cat.children.order_by("id").first()
                if first_child and first_child.image:
                    root_cat.image = first_child.image.name
                    root_cat.save(update_fields=["image"])

        self.stdout.write(self.style.SUCCESS(f"Seeded extra: {stats}"))
