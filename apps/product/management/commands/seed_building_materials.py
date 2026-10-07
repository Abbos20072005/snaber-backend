"""Seed the catalog with professional building-materials data.

Replaces the current demo catalog (categories, products, variants, attributes
and their dependents) with a building-materials taxonomy where every leaf
category owns filterable attributes, so the storefront filters stay relevant.

Usage:
    python manage.py seed_building_materials --confirm
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction


# ---------------------------------------------------------------------------
# Data: (en, ru, uz) triples. Plain strings are language-neutral (grades, sizes).
# ---------------------------------------------------------------------------

UNITS = [
    ("pcs", "шт", "dona"),
    ("kg", "кг", "kg"),
    ("t", "т", "t"),
    ("m", "м", "m"),
    ("m2", "м2", "m2"),
    ("m3", "м3", "m3"),
    ("bag", "мешок", "qop"),
    ("box", "коробка", "quti"),
    ("l", "л", "l"),
    ("roll", "рулон", "rulon"),
    ("set", "комплект", "to'plam"),
    ("sheet", "лист", "varaq"),
]

CATEGORY_IMAGE_POOL = [
    "categories/files/IMG_1356.PNG",
    "categories/files/2026-04-21_09.36.03.jpg",
]

PRODUCT_IMAGE_POOL = [
    "products/files/IMG_8080.PNG",
    "products/files/IMG_8070.HEIC",
]

# -- leaf schema -------------------------------------------------------------
# {
#   "code": str,
#   "n": (en, ru, uz),
#   "attrs": [((en, ru, uz), [value, ...]), ...],
#   "products": [{
#     "n": (en, ru, uz), "moq": int, "unit": str,
#     "lead": (min_days, max_days),
#     "variants": [{"v": {attr_en: value_en}, "price": int, "stock": int}, ...],
#     "chars": [(name, value), ...],
#   }, ...],
# }
# ----------------------------------------------------------------------------

ROOTS = [
    {
        "code": "cement-concrete",
        "n": ("Cement & Concrete", "Цемент и бетон", "Sement va beton"),
        "children": [
            {
                "code": "portland-cement",
                "n": ("Portland Cement", "Портландцемент", "Portlandsement"),
                "attrs": [
                    (
                        ("Brand", "Бренд", "Brend"),
                        ["Akhangaran", "Kuvasay", "Bekabad"],
                    ),
                    (
                        ("Grade", "Марка", "Marka"),
                        ["M400", "M500"],
                    ),
                    (
                        ("Packing", "Фасовка", "Qadoqlash"),
                        ["50 kg bag", "Big-bag 1000 kg"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Akhangaran Portland Cement M500, 50 kg",
                            "Портландцемент Ахангаран М500, 50 кг",
                            "Ohangaron portlandsement M500, 50 kg",
                        ),
                        "moq": 50,
                        "unit": "bag",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Brand": "Akhangaran",
                                    "Grade": "M500",
                                    "Packing": "50 kg bag",
                                },
                                "price": 78000,
                                "stock": 8000,
                            },
                            {
                                "v": {
                                    "Brand": "Akhangaran",
                                    "Grade": "M500",
                                    "Packing": "Big-bag 1000 kg",
                                },
                                "price": 1450000,
                                "stock": 400,
                            },
                        ],
                        "chars": [
                            ("Compressive strength", "42.5 MPa"),
                            ("Setting start", "45 min"),
                            ("Shelf life", "6 months"),
                        ],
                    },
                    {
                        "n": (
                            "Kuvasay Portland Cement M400, 50 kg",
                            "Портландцемент Кувасай М400, 50 кг",
                            "Quvasoy portlandsement M400, 50 kg",
                        ),
                        "moq": 50,
                        "unit": "bag",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Brand": "Kuvasay",
                                    "Grade": "M400",
                                    "Packing": "50 kg bag",
                                },
                                "price": 72000,
                                "stock": 6000,
                            },
                            {
                                "v": {
                                    "Brand": "Kuvasay",
                                    "Grade": "M400",
                                    "Packing": "Big-bag 1000 kg",
                                },
                                "price": 1350000,
                                "stock": 300,
                            },
                        ],
                        "chars": [
                            ("Compressive strength", "32.5 MPa"),
                            ("Setting start", "60 min"),
                            ("Shelf life", "6 months"),
                        ],
                    },
                ],
            },
            {
                "code": "ready-mix",
                "n": ("Ready-Mix Concrete", "Товарный бетон", "Tayyor beton"),
                "attrs": [
                    (
                        ("Class", "Класс", "Sinf"),
                        ["B15", "B20", "B25", "B30"],
                    ),
                    (
                        ("Slump", "Подвижность", "Harakatchanlik"),
                        ["P2", "P3"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Ready-mix concrete B25, slump P3",
                            "Товарный бетон B25, П3",
                            "Tayyor beton B25, P3",
                        ),
                        "moq": 7,
                        "unit": "m3",
                        "lead": (1, 2),
                        "variants": [
                            {
                                "v": {"Class": "B25", "Slump": "P3"},
                                "price": 850000,
                                "stock": 200,
                            },
                            {
                                "v": {"Class": "B30", "Slump": "P3"},
                                "price": 920000,
                                "stock": 150,
                            },
                        ],
                        "chars": [
                            ("Aggregate", "Granite 5-20 mm"),
                            ("Delivery", "Mixer 7 m3"),
                            ("Standard", "GOST 7473"),
                        ],
                    },
                    {
                        "n": (
                            "Ready-mix concrete B15, slump P2",
                            "Товарный бетон B15, П2",
                            "Tayyor beton B15, P2",
                        ),
                        "moq": 7,
                        "unit": "m3",
                        "lead": (1, 2),
                        "variants": [
                            {
                                "v": {"Class": "B15", "Slump": "P2"},
                                "price": 720000,
                                "stock": 200,
                            },
                            {
                                "v": {"Class": "B20", "Slump": "P2"},
                                "price": 780000,
                                "stock": 200,
                            },
                        ],
                        "chars": [
                            ("Aggregate", "Gravel 5-20 mm"),
                            ("Delivery", "Mixer 7 m3"),
                            ("Standard", "GOST 7473"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "bricks-blocks",
        "n": ("Bricks & Blocks", "Кирпич и блоки", "G'isht va bloklar"),
        "children": [
            {
                "code": "ceramic-brick",
                "n": ("Ceramic Brick", "Кирпич керамический", "Sopol g'isht"),
                "attrs": [
                    (
                        ("Size", "Размер", "O'lcham"),
                        ["250x120x65", "250x120x138"],
                    ),
                    (
                        ("Grade", "Марка", "Marka"),
                        ["M100", "M125", "M150"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Single ceramic brick M150, 250x120x65",
                            "Кирпич одинарный М150, 250x120x65",
                            "Yakka sopol g'isht M150, 250x120x65",
                        ),
                        "moq": 1000,
                        "unit": "pcs",
                        "lead": (2, 5),
                        "variants": [
                            {
                                "v": {"Size": "250x120x65", "Grade": "M150"},
                                "price": 2200,
                                "stock": 120000,
                            },
                            {
                                "v": {"Size": "250x120x65", "Grade": "M125"},
                                "price": 1900,
                                "stock": 90000,
                            },
                        ],
                        "chars": [
                            ("Water absorption", "8%"),
                            ("Frost resistance", "F50"),
                            ("Void ratio", "12%"),
                        ],
                    },
                    {
                        "n": (
                            "Double ceramic brick M125, 250x120x138",
                            "Кирпич двойной М125, 250x120x138",
                            "Qo'shaloq sopol g'isht M125, 250x120x138",
                        ),
                        "moq": 1000,
                        "unit": "pcs",
                        "lead": (2, 5),
                        "variants": [
                            {
                                "v": {"Size": "250x120x138", "Grade": "M125"},
                                "price": 3600,
                                "stock": 60000,
                            },
                            {
                                "v": {"Size": "250x120x138", "Grade": "M100"},
                                "price": 3200,
                                "stock": 50000,
                            },
                        ],
                        "chars": [
                            ("Water absorption", "9%"),
                            ("Frost resistance", "F35"),
                            ("Void ratio", "30%"),
                        ],
                    },
                ],
            },
            {
                "code": "aerated-block",
                "n": ("Aerated Block", "Газоблок", "Gazoblok"),
                "attrs": [
                    (
                        ("Density", "Плотность", "Zichlik"),
                        ["D400", "D500", "D600"],
                    ),
                    (
                        ("Size", "Размер", "O'lcham"),
                        ["600x200x100", "600x200x200", "600x200x300"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Aerated wall block D500, 600x200x300",
                            "Газоблок стеновой D500, 600x200x300",
                            "Devor gazoblogi D500, 600x200x300",
                        ),
                        "moq": 100,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Density": "D500", "Size": "600x200x300"},
                                "price": 28000,
                                "stock": 15000,
                            },
                            {
                                "v": {"Density": "D600", "Size": "600x200x300"},
                                "price": 30000,
                                "stock": 10000,
                            },
                        ],
                        "chars": [
                            ("Thermal conductivity", "0.12 W/mK"),
                            ("Compressive strength", "B2.5"),
                            ("Standard", "GOST 31360"),
                        ],
                    },
                    {
                        "n": (
                            "Aerated partition block D400, 600x200x100",
                            "Газоблок перегородочный D400, 600x200x100",
                            "To'siq gazoblogi D400, 600x200x100",
                        ),
                        "moq": 100,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Density": "D400", "Size": "600x200x100"},
                                "price": 14000,
                                "stock": 20000,
                            },
                            {
                                "v": {"Density": "D500", "Size": "600x200x100"},
                                "price": 15000,
                                "stock": 15000,
                            },
                        ],
                        "chars": [
                            ("Thermal conductivity", "0.10 W/mK"),
                            ("Compressive strength", "B1.5"),
                            ("Standard", "GOST 31360"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "steel-metal",
        "n": ("Steel & Metal", "Металлопрокат", "Metall prokat"),
        "children": [
            {
                "code": "rebar",
                "n": ("Rebar", "Арматура", "Armatura"),
                "attrs": [
                    (
                        ("Diameter", "Диаметр", "Diametr"),
                        ["10 mm", "12 mm", "14 mm", "16 mm", "20 mm"],
                    ),
                    (
                        ("Grade", "Класс", "Sinf"),
                        ["A400", "A500C"],
                    ),
                    (
                        ("Length", "Длина", "Uzunlik"),
                        ["6 m", "12 m"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Rebar A500C 12 mm, 12 m",
                            "Арматура А500С 12 мм, 12 м",
                            "Armatura A500C 12 mm, 12 m",
                        ),
                        "moq": 1,
                        "unit": "t",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Diameter": "12 mm",
                                    "Grade": "A500C",
                                    "Length": "12 m",
                                },
                                "price": 8400000,
                                "stock": 120,
                            },
                            {
                                "v": {
                                    "Diameter": "14 mm",
                                    "Grade": "A500C",
                                    "Length": "12 m",
                                },
                                "price": 8350000,
                                "stock": 100,
                            },
                        ],
                        "chars": [
                            ("Standard", "GOST 34028"),
                            ("Yield strength", "500 MPa"),
                            ("Bundle weight", "2.5 t"),
                        ],
                    },
                    {
                        "n": (
                            "Rebar A400 10 mm, 12 m",
                            "Арматура А400 10 мм, 12 м",
                            "Armatura A400 10 mm, 12 m",
                        ),
                        "moq": 1,
                        "unit": "t",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Diameter": "10 mm",
                                    "Grade": "A400",
                                    "Length": "12 m",
                                },
                                "price": 8600000,
                                "stock": 80,
                            },
                        ],
                        "chars": [
                            ("Standard", "GOST 5781"),
                            ("Yield strength", "400 MPa"),
                            ("Bundle weight", "1.8 t"),
                        ],
                    },
                ],
            },
            {
                "code": "profile-pipe",
                "n": ("Profile Pipe", "Труба профильная", "Profil quvur"),
                "attrs": [
                    (
                        ("Size", "Сечение", "Kesim"),
                        ["20x20", "40x20", "60x40"],
                    ),
                    (
                        ("Wall", "Стенка", "Devor"),
                        ["1.5 mm", "2.0 mm"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Profile pipe 40x20x2.0, 6 m",
                            "Труба профильная 40x20x2.0, 6 м",
                            "Profil quvur 40x20x2.0, 6 m",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Size": "40x20", "Wall": "2.0 mm"},
                                "price": 95000,
                                "stock": 2000,
                            },
                            {
                                "v": {"Size": "40x20", "Wall": "1.5 mm"},
                                "price": 78000,
                                "stock": 1500,
                            },
                        ],
                        "chars": [
                            ("Steel grade", "St3sp"),
                            ("Length", "6 m"),
                            ("Standard", "GOST 8639"),
                        ],
                    },
                    {
                        "n": (
                            "Profile pipe 60x40x2.0, 6 m",
                            "Труба профильная 60x40x2.0, 6 м",
                            "Profil quvur 60x40x2.0, 6 m",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Size": "60x40", "Wall": "2.0 mm"},
                                "price": 145000,
                                "stock": 1200,
                            },
                        ],
                        "chars": [
                            ("Steel grade", "St3sp"),
                            ("Length", "6 m"),
                            ("Standard", "GOST 8639"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "lumber-timber",
        "n": ("Lumber & Timber", "Пиломатериалы", "Yog'och materiallar"),
        "children": [
            {
                "code": "edged-board",
                "n": ("Edged Board", "Доска обрезная", "Kesilgan taxta"),
                "attrs": [
                    (
                        ("Species", "Порода", "Daraxt turi"),
                        [
                            ("Pine", "Сосна", "Qarag'ay"),
                            ("Spruce", "Ель", "Yel"),
                        ],
                    ),
                    (
                        ("Size", "Сечение", "Kesim"),
                        ["25x100", "40x150", "50x200"],
                    ),
                    (
                        ("Grade", "Сорт", "Nav"),
                        [("1st", "1-й", "1-nav"), ("2nd", "2-й", "2-nav")],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Pine edged board 50x200, 1st grade",
                            "Доска сосна 50x200, 1 сорт",
                            "Qarag'ay kesilgan taxta 50x200, 1-nav",
                        ),
                        "moq": 2,
                        "unit": "m3",
                        "lead": (2, 7),
                        "variants": [
                            {
                                "v": {
                                    "Species": "Pine",
                                    "Size": "50x200",
                                    "Grade": "1st",
                                },
                                "price": 4200000,
                                "stock": 60,
                            },
                            {
                                "v": {
                                    "Species": "Pine",
                                    "Size": "50x200",
                                    "Grade": "2nd",
                                },
                                "price": 3600000,
                                "stock": 40,
                            },
                        ],
                        "chars": [
                            ("Moisture", "18%"),
                            ("Length", "6 m"),
                            ("Standard", "GOST 8486"),
                        ],
                    },
                    {
                        "n": (
                            "Spruce edged board 25x100, 1st grade",
                            "Доска ель 25x100, 1 сорт",
                            "Yel kesilgan taxta 25x100, 1-nav",
                        ),
                        "moq": 2,
                        "unit": "m3",
                        "lead": (2, 7),
                        "variants": [
                            {
                                "v": {
                                    "Species": "Spruce",
                                    "Size": "25x100",
                                    "Grade": "1st",
                                },
                                "price": 3800000,
                                "stock": 50,
                            },
                        ],
                        "chars": [
                            ("Moisture", "18%"),
                            ("Length", "6 m"),
                            ("Standard", "GOST 8486"),
                        ],
                    },
                ],
            },
            {
                "code": "plywood",
                "n": ("Plywood", "Фанера", "Fanera"),
                "attrs": [
                    (
                        ("Thickness", "Толщина", "Qalinlik"),
                        ["9 mm", "12 mm", "15 mm", "18 mm"],
                    ),
                    (
                        ("Grade", "Марка", "Marka"),
                        ["FC", "FSF"],
                    ),
                    (
                        ("Sheet", "Формат", "Bichim"),
                        ["1525x1525", "2440x1220"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "FSF plywood 18 mm, 2440x1220",
                            "Фанера ФСФ 18 мм, 2440x1220",
                            "FSF fanera 18 mm, 2440x1220",
                        ),
                        "moq": 20,
                        "unit": "sheet",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {
                                    "Thickness": "18 mm",
                                    "Grade": "FSF",
                                    "Sheet": "2440x1220",
                                },
                                "price": 420000,
                                "stock": 800,
                            },
                            {
                                "v": {
                                    "Thickness": "15 mm",
                                    "Grade": "FSF",
                                    "Sheet": "2440x1220",
                                },
                                "price": 360000,
                                "stock": 600,
                            },
                        ],
                        "chars": [
                            ("Emission class", "E1"),
                            ("Moisture resistance", "High"),
                            ("Standard", "GOST 3916"),
                        ],
                    },
                    {
                        "n": (
                            "FC plywood 12 mm, 1525x1525",
                            "Фанера ФК 12 мм, 1525x1525",
                            "FK fanera 12 mm, 1525x1525",
                        ),
                        "moq": 20,
                        "unit": "sheet",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {
                                    "Thickness": "12 mm",
                                    "Grade": "FC",
                                    "Sheet": "1525x1525",
                                },
                                "price": 210000,
                                "stock": 1000,
                            },
                        ],
                        "chars": [
                            ("Emission class", "E1"),
                            ("Use", "Interior"),
                            ("Standard", "GOST 3916"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "drywall-plaster",
        "n": (
            "Drywall & Plaster",
            "Гипсокартон и смеси",
            "Gipsokarton va aralashmalar",
        ),
        "children": [
            {
                "code": "gypsum-board",
                "n": ("Gypsum Board", "Гипсокартон", "Gipsokarton"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Standard", "Стандарт", "Standart"),
                            (
                                "Moisture-resistant",
                                "Влагостойкий",
                                "Namga chidamli",
                            ),
                            (
                                "Fire-resistant",
                                "Огнестойкий",
                                "Olovga chidamli",
                            ),
                        ],
                    ),
                    (
                        ("Size", "Размер", "O'lcham"),
                        ["2500x1200x9.5", "2500x1200x12.5"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Standard gypsum board 2500x1200x12.5",
                            "Гипсокартон стандартный 2500x1200x12.5",
                            "Standart gipsokarton 2500x1200x12.5",
                        ),
                        "moq": 30,
                        "unit": "sheet",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Type": "Standard",
                                    "Size": "2500x1200x12.5",
                                },
                                "price": 95000,
                                "stock": 3000,
                            },
                            {
                                "v": {
                                    "Type": "Standard",
                                    "Size": "2500x1200x9.5",
                                },
                                "price": 85000,
                                "stock": 2000,
                            },
                        ],
                        "chars": [
                            ("Edge", "Tapered"),
                            ("Weight", "29 kg"),
                            ("Standard", "GOST 6266"),
                        ],
                    },
                    {
                        "n": (
                            "Moisture-resistant gypsum board 2500x1200x12.5",
                            "Гипсокартон влагостойкий 2500x1200x12.5",
                            "Namga chidamli gipsokarton 2500x1200x12.5",
                        ),
                        "moq": 30,
                        "unit": "sheet",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {
                                    "Type": "Moisture-resistant",
                                    "Size": "2500x1200x12.5",
                                },
                                "price": 115000,
                                "stock": 2000,
                            },
                        ],
                        "chars": [
                            ("Edge", "Tapered"),
                            ("Use", "Wet rooms"),
                            ("Standard", "GOST 6266"),
                        ],
                    },
                ],
            },
            {
                "code": "dry-mixes",
                "n": ("Dry Mixes", "Сухие смеси", "Quruq aralashmalar"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Plaster", "Штукатурка", "Shivok"),
                            ("Putty", "Шпаклёвка", "Shpaklyovka"),
                            (
                                "Tile adhesive",
                                "Клей для плитки",
                                "Kafel yelimi",
                            ),
                        ],
                    ),
                    (
                        ("Packing", "Фасовка", "Qadoqlash"),
                        ["25 kg", "30 kg"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Gypsum plaster 30 kg",
                            "Штукатурка гипсовая 30 кг",
                            "Gips shivok 30 kg",
                        ),
                        "moq": 40,
                        "unit": "bag",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Plaster", "Packing": "30 kg"},
                                "price": 68000,
                                "stock": 5000,
                            },
                            {
                                "v": {"Type": "Plaster", "Packing": "25 kg"},
                                "price": 58000,
                                "stock": 3000,
                            },
                        ],
                        "chars": [
                            ("Consumption", "8.5 kg/m2"),
                            ("Layer", "5-50 mm"),
                            ("Pot life", "90 min"),
                        ],
                    },
                    {
                        "n": (
                            "Tile adhesive C1, 25 kg",
                            "Клей для плитки C1, 25 кг",
                            "Kafel yelimi C1, 25 kg",
                        ),
                        "moq": 40,
                        "unit": "bag",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Tile adhesive", "Packing": "25 kg"},
                                "price": 75000,
                                "stock": 4000,
                            },
                        ],
                        "chars": [
                            ("Consumption", "3 kg/m2"),
                            ("Open time", "20 min"),
                            ("Standard", "EN 12004 C1"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "insulation",
        "n": (
            "Insulation",
            "Теплоизоляция",
            "Issiqlik izolyatsiyasi",
        ),
        "children": [
            {
                "code": "mineral-wool",
                "n": ("Mineral Wool", "Минеральная вата", "Mineral paxta"),
                "attrs": [
                    (
                        ("Density", "Плотность", "Zichlik"),
                        ["35 kg/m3", "50 kg/m3", "80 kg/m3"],
                    ),
                    (
                        ("Thickness", "Толщина", "Qalinlik"),
                        ["50 mm", "100 mm"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Mineral wool slab 50 kg/m3, 100 mm",
                            "Минвата плита 50 кг/м3, 100 мм",
                            "Mineral paxta plita 50 kg/m3, 100 mm",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Density": "50 kg/m3", "Thickness": "100 mm"},
                                "price": 95000,
                                "stock": 3000,
                            },
                            {
                                "v": {"Density": "50 kg/m3", "Thickness": "50 mm"},
                                "price": 55000,
                                "stock": 3000,
                            },
                        ],
                        "chars": [
                            ("Thermal conductivity", "0.037 W/mK"),
                            ("Fire class", "NG"),
                            ("Size", "1000x600 mm"),
                        ],
                    },
                    {
                        "n": (
                            "Mineral wool slab 35 kg/m3, 50 mm",
                            "Минвата плита 35 кг/м3, 50 мм",
                            "Mineral paxta plita 35 kg/m3, 50 mm",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Density": "35 kg/m3", "Thickness": "50 mm"},
                                "price": 42000,
                                "stock": 4000,
                            },
                        ],
                        "chars": [
                            ("Thermal conductivity", "0.039 W/mK"),
                            ("Fire class", "NG"),
                            ("Size", "1000x600 mm"),
                        ],
                    },
                ],
            },
            {
                "code": "xps-boards",
                "n": ("XPS Boards", "Пенополистирол XPS", "XPS penopolistirol"),
                "attrs": [
                    (
                        ("Thickness", "Толщина", "Qalinlik"),
                        ["20 mm", "30 mm", "50 mm", "100 mm"],
                    ),
                    (
                        ("Size", "Формат", "Bichim"),
                        ["1200x600"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "XPS board 50 mm, 1200x600",
                            "XPS плита 50 мм, 1200x600",
                            "XPS plita 50 mm, 1200x600",
                        ),
                        "moq": 30,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Thickness": "50 mm", "Size": "1200x600"},
                                "price": 88000,
                                "stock": 2500,
                            },
                            {
                                "v": {"Thickness": "30 mm", "Size": "1200x600"},
                                "price": 58000,
                                "stock": 2500,
                            },
                        ],
                        "chars": [
                            ("Compressive strength", "250 kPa"),
                            ("Thermal conductivity", "0.032 W/mK"),
                            ("Edge", "L-shaped"),
                        ],
                    },
                    {
                        "n": (
                            "XPS board 100 mm, 1200x600",
                            "XPS плита 100 мм, 1200x600",
                            "XPS plita 100 mm, 1200x600",
                        ),
                        "moq": 30,
                        "unit": "pcs",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Thickness": "100 mm", "Size": "1200x600"},
                                "price": 165000,
                                "stock": 1200,
                            },
                        ],
                        "chars": [
                            ("Compressive strength", "300 kPa"),
                            ("Thermal conductivity", "0.033 W/mK"),
                            ("Edge", "L-shaped"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "roofing",
        "n": ("Roofing", "Кровля", "Tom yopish materiallari"),
        "children": [
            {
                "code": "metal-tile",
                "n": ("Metal Tile", "Металлочерепица", "Metall cherepitsa"),
                "attrs": [
                    (
                        ("Profile", "Профиль", "Profil"),
                        ["Monterrey", "Cascade"],
                    ),
                    (
                        ("Coating", "Покрытие", "Qoplama"),
                        ["Polyester", "Pural"],
                    ),
                    (
                        ("Color", "Цвет", "Rang"),
                        [
                            ("Red", "Красный", "Qizil"),
                            ("Brown", "Коричневый", "Jigarrang"),
                            ("Green", "Зелёный", "Yashil"),
                        ],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Metal tile Monterrey, Polyester, red",
                            "Металлочерепица Монтеррей, полиэстер, красная",
                            "Metall cherepitsa Monterrey, polyester, qizil",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (3, 10),
                        "variants": [
                            {
                                "v": {
                                    "Profile": "Monterrey",
                                    "Coating": "Polyester",
                                    "Color": "Red",
                                },
                                "price": 135000,
                                "stock": 5000,
                            },
                            {
                                "v": {
                                    "Profile": "Monterrey",
                                    "Coating": "Polyester",
                                    "Color": "Brown",
                                },
                                "price": 135000,
                                "stock": 4000,
                            },
                        ],
                        "chars": [
                            ("Steel thickness", "0.5 mm"),
                            ("Coating thickness", "25 mkm"),
                            ("Warranty", "10 years"),
                        ],
                    },
                    {
                        "n": (
                            "Metal tile Cascade, Pural, brown",
                            "Металлочерепица Каскад, пурал, коричневая",
                            "Metall cherepitsa Kaskad, pural, jigarrang",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (3, 10),
                        "variants": [
                            {
                                "v": {
                                    "Profile": "Cascade",
                                    "Coating": "Pural",
                                    "Color": "Brown",
                                },
                                "price": 185000,
                                "stock": 3000,
                            },
                        ],
                        "chars": [
                            ("Steel thickness", "0.5 mm"),
                            ("Coating thickness", "50 mkm"),
                            ("Warranty", "20 years"),
                        ],
                    },
                ],
            },
            {
                "code": "corrugated-sheet",
                "n": ("Corrugated Sheet", "Профнастил", "Profnastil"),
                "attrs": [
                    (
                        ("Profile", "Профиль", "Profil"),
                        ["C8", "C20", "H57"],
                    ),
                    (
                        ("Thickness", "Толщина", "Qalinlik"),
                        ["0.4 mm", "0.5 mm", "0.7 mm"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Corrugated sheet C20, 0.5 mm",
                            "Профнастил С20, 0.5 мм",
                            "Profnastil C20, 0.5 mm",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (2, 7),
                        "variants": [
                            {
                                "v": {"Profile": "C20", "Thickness": "0.5 mm"},
                                "price": 110000,
                                "stock": 6000,
                            },
                            {
                                "v": {"Profile": "C20", "Thickness": "0.4 mm"},
                                "price": 95000,
                                "stock": 5000,
                            },
                        ],
                        "chars": [
                            ("Coating", "Polyester 25 mkm"),
                            ("Useful width", "1100 mm"),
                            ("Standard", "GOST 24045"),
                        ],
                    },
                    {
                        "n": (
                            "Corrugated sheet H57, 0.7 mm",
                            "Профнастил Н57, 0.7 мм",
                            "Profnastil H57, 0.7 mm",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (2, 7),
                        "variants": [
                            {
                                "v": {"Profile": "H57", "Thickness": "0.7 mm"},
                                "price": 155000,
                                "stock": 4000,
                            },
                        ],
                        "chars": [
                            ("Coating", "Polyester 25 mkm"),
                            ("Useful width", "750 mm"),
                            ("Standard", "GOST 24045"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "flooring-tile",
        "n": ("Flooring & Tile", "Полы и плитка", "Pol va kafel"),
        "children": [
            {
                "code": "ceramic-tile",
                "n": ("Ceramic Tile", "Керамическая плитка", "Keramik kafel"),
                "attrs": [
                    (
                        ("Size", "Размер", "O'lcham"),
                        ["300x300", "600x600", "1200x600"],
                    ),
                    (
                        ("Surface", "Поверхность", "Sirt"),
                        [("Matt", "Матовая", "Xira"), ("Glossy", "Глянцевая", "Yaltiroq")],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Floor tile 600x600, matt",
                            "Плитка напольная 600x600, матовая",
                            "Pol kafeli 600x600, xira",
                        ),
                        "moq": 5,
                        "unit": "m2",
                        "lead": (1, 5),
                        "variants": [
                            {
                                "v": {"Size": "600x600", "Surface": "Matt"},
                                "price": 145000,
                                "stock": 2000,
                            },
                            {
                                "v": {"Size": "600x600", "Surface": "Glossy"},
                                "price": 155000,
                                "stock": 1500,
                            },
                        ],
                        "chars": [
                            ("Wear class", "PEI IV"),
                            ("Slip resistance", "R10"),
                            ("Thickness", "9 mm"),
                        ],
                    },
                    {
                        "n": (
                            "Porcelain tile 1200x600, glossy",
                            "Керамогранит 1200x600, глянцевый",
                            "Keramogranit 1200x600, yaltiroq",
                        ),
                        "moq": 5,
                        "unit": "m2",
                        "lead": (1, 5),
                        "variants": [
                            {
                                "v": {"Size": "1200x600", "Surface": "Glossy"},
                                "price": 195000,
                                "stock": 1200,
                            },
                        ],
                        "chars": [
                            ("Wear class", "PEI V"),
                            ("Water absorption", "0.1%"),
                            ("Thickness", "9 mm"),
                        ],
                    },
                ],
            },
            {
                "code": "laminate",
                "n": ("Laminate", "Ламинат", "Laminat"),
                "attrs": [
                    (
                        ("Class", "Класс", "Sinf"),
                        ["31", "32", "33"],
                    ),
                    (
                        ("Thickness", "Толщина", "Qalinlik"),
                        ["8 mm", "10 mm", "12 mm"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Laminate class 33, 12 mm",
                            "Ламинат 33 класс, 12 мм",
                            "Laminat 33-sinf, 12 mm",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Class": "33", "Thickness": "12 mm"},
                                "price": 165000,
                                "stock": 1500,
                            },
                            {
                                "v": {"Class": "33", "Thickness": "10 mm"},
                                "price": 145000,
                                "stock": 1200,
                            },
                        ],
                        "chars": [
                            ("Lock", "Click"),
                            ("Warranty", "25 years"),
                            ("Use", "Commercial"),
                        ],
                    },
                    {
                        "n": (
                            "Laminate class 32, 8 mm",
                            "Ламинат 32 класс, 8 мм",
                            "Laminat 32-sinf, 8 mm",
                        ),
                        "moq": 10,
                        "unit": "m2",
                        "lead": (1, 4),
                        "variants": [
                            {
                                "v": {"Class": "32", "Thickness": "8 mm"},
                                "price": 110000,
                                "stock": 2000,
                            },
                        ],
                        "chars": [
                            ("Lock", "Click"),
                            ("Warranty", "15 years"),
                            ("Use", "Residential"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "paints-coatings",
        "n": ("Paints & Coatings", "Краски", "Bo'yoqlar"),
        "children": [
            {
                "code": "interior-paint",
                "n": ("Interior Paint", "Интерьерная краска", "Ichki bo'yoq"),
                "attrs": [
                    (
                        ("Volume", "Объём", "Hajm"),
                        ["2.5 L", "10 L", "20 L"],
                    ),
                    (
                        ("Finish", "Финиш", "Yuzasi"),
                        [("Matt", "Матовая", "Xira"), ("Silk", "Шелковистая", "Ipakdek")],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Interior acrylic paint, white matt",
                            "Краска интерьерная белая матовая",
                            "Ichki oq xira bo'yoq",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Volume": "10 L", "Finish": "Matt"},
                                "price": 320000,
                                "stock": 800,
                            },
                            {
                                "v": {"Volume": "20 L", "Finish": "Matt"},
                                "price": 590000,
                                "stock": 500,
                            },
                        ],
                        "chars": [
                            ("Consumption", "10 m2/L"),
                            ("Drying", "2 hours"),
                            ("Base", "Acrylic"),
                        ],
                    },
                    {
                        "n": (
                            "Interior silk paint, white",
                            "Краска интерьерная белая шелковистая",
                            "Ichki oq ipakdek bo'yoq",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Volume": "10 L", "Finish": "Silk"},
                                "price": 360000,
                                "stock": 600,
                            },
                        ],
                        "chars": [
                            ("Consumption", "11 m2/L"),
                            ("Washability", "Class 1"),
                            ("Base", "Acrylic"),
                        ],
                    },
                ],
            },
            {
                "code": "primer",
                "n": ("Primer", "Грунтовка", "Gruntovka"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Acrylic", "Акриловая", "Akril"),
                            (
                                "Deep-penetrating",
                                "Глубокого проникновения",
                                "Chuqur kiruvchi",
                            ),
                        ],
                    ),
                    (
                        ("Volume", "Объём", "Hajm"),
                        ["5 L", "10 L"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Acrylic primer, 10 L",
                            "Грунтовка акриловая, 10 л",
                            "Akril gruntovka, 10 l",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Acrylic", "Volume": "10 L"},
                                "price": 145000,
                                "stock": 1000,
                            },
                            {
                                "v": {"Type": "Acrylic", "Volume": "5 L"},
                                "price": 85000,
                                "stock": 800,
                            },
                        ],
                        "chars": [
                            ("Consumption", "8 m2/L"),
                            ("Drying", "1 hour"),
                            ("Base", "Acrylic dispersion"),
                        ],
                    },
                    {
                        "n": (
                            "Deep-penetrating primer, 5 L",
                            "Грунтовка глубокого проникновения, 5 л",
                            "Chuqur kiruvchi gruntovka, 5 l",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Deep-penetrating", "Volume": "5 L"},
                                "price": 95000,
                                "stock": 900,
                            },
                        ],
                        "chars": [
                            ("Consumption", "6 m2/L"),
                            ("Drying", "2 hours"),
                            ("Use", "Weak substrates"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "plumbing",
        "n": ("Plumbing", "Сантехника", "Santexnika"),
        "children": [
            {
                "code": "pp-pipes",
                "n": ("PP Pipes", "Трубы полипропиленовые", "Polipropilen quvurlar"),
                "attrs": [
                    (
                        ("Diameter", "Диаметр", "Diametr"),
                        ["20 mm", "25 mm", "32 mm", "40 mm"],
                    ),
                    (
                        ("Pressure", "Давление", "Bosim"),
                        ["PN16", "PN20"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "PP pipe 25 mm PN20, 4 m",
                            "Труба ПП 25 мм PN20, 4 м",
                            "PP quvur 25 mm PN20, 4 m",
                        ),
                        "moq": 25,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Diameter": "25 mm", "Pressure": "PN20"},
                                "price": 42000,
                                "stock": 3000,
                            },
                            {
                                "v": {"Diameter": "25 mm", "Pressure": "PN16"},
                                "price": 36000,
                                "stock": 2500,
                            },
                        ],
                        "chars": [
                            ("Material", "PPR-80"),
                            ("Length", "4 m"),
                            ("Standard", "GOST 32415"),
                        ],
                    },
                    {
                        "n": (
                            "PP pipe 32 mm PN16, 4 m",
                            "Труба ПП 32 мм PN16, 4 м",
                            "PP quvur 32 mm PN16, 4 m",
                        ),
                        "moq": 25,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Diameter": "32 mm", "Pressure": "PN16"},
                                "price": 52000,
                                "stock": 2000,
                            },
                        ],
                        "chars": [
                            ("Material", "PPR-80"),
                            ("Length", "4 m"),
                            ("Standard", "GOST 32415"),
                        ],
                    },
                ],
            },
            {
                "code": "faucets",
                "n": ("Faucets", "Смесители", "Smesitellar"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Basin", "Для раковины", "Rakovina uchun"),
                            ("Shower", "Для душа", "Dush uchun"),
                            ("Kitchen", "Для кухни", "Oshxona uchun"),
                        ],
                    ),
                    (
                        ("Material", "Материал", "Material"),
                        [("Brass", "Латунь", "Latun")],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Brass basin faucet",
                            "Смеситель для раковины, латунь",
                            "Latun rakovina smesiteli",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (2, 5),
                        "variants": [
                            {
                                "v": {"Type": "Basin", "Material": "Brass"},
                                "price": 650000,
                                "stock": 300,
                            },
                        ],
                        "chars": [
                            ("Cartridge", "Ceramic 35 mm"),
                            ("Coating", "Chrome"),
                            ("Warranty", "5 years"),
                        ],
                    },
                    {
                        "n": (
                            "Brass shower faucet",
                            "Смеситель для душа, латунь",
                            "Latun dush smesiteli",
                        ),
                        "moq": 5,
                        "unit": "pcs",
                        "lead": (2, 5),
                        "variants": [
                            {
                                "v": {"Type": "Shower", "Material": "Brass"},
                                "price": 850000,
                                "stock": 250,
                            },
                            {
                                "v": {"Type": "Kitchen", "Material": "Brass"},
                                "price": 750000,
                                "stock": 250,
                            },
                        ],
                        "chars": [
                            ("Cartridge", "Ceramic 40 mm"),
                            ("Coating", "Chrome"),
                            ("Warranty", "5 years"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "electrical",
        "n": ("Electrical", "Электрика", "Elektr jihozlari"),
        "children": [
            {
                "code": "cables",
                "n": ("Cables", "Кабели", "Kabellar"),
                "attrs": [
                    (
                        ("Cross-section", "Сечение", "Kesim"),
                        ["1.5 mm2", "2.5 mm2", "4.0 mm2"],
                    ),
                    (
                        ("Cores", "Жилы", "Tomirlar"),
                        ["2", "3"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Copper cable VVG 3x2.5",
                            "Кабель медный ВВГ 3x2.5",
                            "Mis kabel VVG 3x2.5",
                        ),
                        "moq": 50,
                        "unit": "m",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Cross-section": "2.5 mm2", "Cores": "3"},
                                "price": 28000,
                                "stock": 10000,
                            },
                            {
                                "v": {"Cross-section": "1.5 mm2", "Cores": "3"},
                                "price": 19000,
                                "stock": 10000,
                            },
                        ],
                        "chars": [
                            ("Voltage", "660 V"),
                            ("Insulation", "PVC"),
                            ("Standard", "GOST 31996"),
                        ],
                    },
                    {
                        "n": (
                            "Copper cable VVG 2x1.5",
                            "Кабель медный ВВГ 2x1.5",
                            "Mis kabel VVG 2x1.5",
                        ),
                        "moq": 50,
                        "unit": "m",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Cross-section": "1.5 mm2", "Cores": "2"},
                                "price": 14000,
                                "stock": 12000,
                            },
                        ],
                        "chars": [
                            ("Voltage", "660 V"),
                            ("Insulation", "PVC"),
                            ("Standard", "GOST 31996"),
                        ],
                    },
                ],
            },
            {
                "code": "sockets-switches",
                "n": (
                    "Sockets & Switches",
                    "Розетки и выключатели",
                    "Rozetka va viklyuchatellar",
                ),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Socket", "Розетка", "Rozetka"),
                            ("Switch", "Выключатель", "Viklyuchatel"),
                        ],
                    ),
                    (
                        ("Color", "Цвет", "Rang"),
                        [("White", "Белый", "Oq"), ("Beige", "Бежевый", "Bej")],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Grounded socket, white",
                            "Розетка с заземлением, белая",
                            "Yerga ulangan rozetka, oq",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Socket", "Color": "White"},
                                "price": 55000,
                                "stock": 2000,
                            },
                            {
                                "v": {"Type": "Socket", "Color": "Beige"},
                                "price": 55000,
                                "stock": 1500,
                            },
                        ],
                        "chars": [
                            ("Current", "16 A"),
                            ("Mounting", "Flush"),
                            ("Standard", "IEC 60884"),
                        ],
                    },
                    {
                        "n": (
                            "Single switch, beige",
                            "Выключатель одинарный, бежевый",
                            "Yakka viklyuchatel, bej",
                        ),
                        "moq": 20,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Type": "Switch", "Color": "Beige"},
                                "price": 48000,
                                "stock": 2000,
                            },
                        ],
                        "chars": [
                            ("Current", "10 A"),
                            ("Mounting", "Flush"),
                            ("Standard", "IEC 60669"),
                        ],
                    },
                ],
            },
        ],
    },
    {
        "code": "tools-equipment",
        "n": ("Tools & Equipment", "Инструменты", "Asboblar"),
        "children": [
            {
                "code": "power-tools",
                "n": ("Power Tools", "Электроинструмент", "Elektr asboblar"),
                "attrs": [
                    (
                        ("Type", "Тип", "Tur"),
                        [
                            ("Drill", "Дрель", "Drel"),
                            ("Angle grinder", "Болгарка", "Bolgarka"),
                            ("Perforator", "Перфоратор", "Perforator"),
                        ],
                    ),
                    (
                        ("Power", "Мощность", "Quvvat"),
                        ["600 W", "800 W", "1200 W"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Rotary hammer 800 W, SDS-plus",
                            "Перфоратор 800 Вт, SDS-plus",
                            "Perforator 800 W, SDS-plus",
                        ),
                        "moq": 2,
                        "unit": "pcs",
                        "lead": (2, 6),
                        "variants": [
                            {
                                "v": {"Type": "Perforator", "Power": "800 W"},
                                "price": 1450000,
                                "stock": 150,
                            },
                        ],
                        "chars": [
                            ("Impact energy", "2.8 J"),
                            ("Chuck", "SDS-plus"),
                            ("Warranty", "1 year"),
                        ],
                    },
                    {
                        "n": (
                            "Angle grinder 1200 W, 125 mm",
                            "Болгарка 1200 Вт, 125 мм",
                            "Bolgarka 1200 W, 125 mm",
                        ),
                        "moq": 2,
                        "unit": "pcs",
                        "lead": (2, 6),
                        "variants": [
                            {
                                "v": {"Type": "Angle grinder", "Power": "1200 W"},
                                "price": 980000,
                                "stock": 200,
                            },
                            {
                                "v": {"Type": "Drill", "Power": "600 W"},
                                "price": 720000,
                                "stock": 180,
                            },
                        ],
                        "chars": [
                            ("Disc", "125 mm"),
                            ("Speed", "11000 rpm"),
                            ("Warranty", "1 year"),
                        ],
                    },
                ],
            },
            {
                "code": "cutting-discs",
                "n": ("Cutting Discs", "Отрезные диски", "Kesish disklari"),
                "attrs": [
                    (
                        ("Purpose", "Назначение", "Maqsad"),
                        [
                            ("Metal", "По металлу", "Metall uchun"),
                            ("Stone", "По камню", "Tosh uchun"),
                        ],
                    ),
                    (
                        ("Diameter", "Диаметр", "Diametr"),
                        ["115 mm", "125 mm", "230 mm"],
                    ),
                ],
                "products": [
                    {
                        "n": (
                            "Metal cutting disc 125 mm",
                            "Диск отрезной по металлу 125 мм",
                            "Metall kesish diski 125 mm",
                        ),
                        "moq": 50,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Purpose": "Metal", "Diameter": "125 mm"},
                                "price": 18000,
                                "stock": 5000,
                            },
                            {
                                "v": {"Purpose": "Metal", "Diameter": "230 mm"},
                                "price": 32000,
                                "stock": 3000,
                            },
                        ],
                        "chars": [
                            ("Thickness", "1.0 mm"),
                            ("Max speed", "12250 rpm"),
                            ("Standard", "EN 12413"),
                        ],
                    },
                    {
                        "n": (
                            "Stone cutting disc 230 mm",
                            "Диск отрезной по камню 230 мм",
                            "Tosh kesish diski 230 mm",
                        ),
                        "moq": 50,
                        "unit": "pcs",
                        "lead": (1, 3),
                        "variants": [
                            {
                                "v": {"Purpose": "Stone", "Diameter": "230 mm"},
                                "price": 38000,
                                "stock": 2500,
                            },
                        ],
                        "chars": [
                            ("Thickness", "1.9 mm"),
                            ("Max speed", "6650 rpm"),
                            ("Standard", "EN 12413"),
                        ],
                    },
                ],
            },
        ],
    },
]


def _t(value):
    """Normalize a value entry to an (en, ru, uz) triple."""
    if isinstance(value, (list, tuple)):
        en, ru, uz = value
        return en, ru, uz
    return value, value, value


class Command(BaseCommand):
    help = "Replace the demo catalog with building-materials seed data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required flag: wipe current catalog data and reseed.",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "Refusing to wipe data without --confirm. "
                    "Run: python manage.py seed_building_materials --confirm"
                )
            )
            return

        from django.contrib.auth import get_user_model

        from apps.company.models import Company
        from apps.order.models import Order, OrderItem, RFQOrderItemAttribute
        from apps.product.models import (
            Attribute,
            AttributeValue,
            Cart,
            CartItem,
            Characteristic,
            CharacteristicConstructor,
            Favourite,
            Category,
            Product,
            ProductAttributeValue,
            ProductAttributeValueConstructor,
            ProductConstructor,
            Unit,
            Variant,
            VariantAttributeStock,
            VariantAttributeStockConstructor,
            VariantConstructor,
            VariantMedia,
            VariantMediaConstructor,
        )
        from apps.review.models import Comment, CommentImage

        with transaction.atomic():
            wiped = {}
            # Dependents first (leaf -> root).
            wiped["rfq_attributes"] = RFQOrderItemAttribute.objects.all().delete()[0]
            wiped["order_items"] = OrderItem.objects.all().delete()[0]
            wiped["orders"] = Order.objects.all().delete()[0]
            wiped["comment_images"] = CommentImage.objects.all().delete()[0]
            wiped["comments"] = Comment.objects.all().delete()[0]
            wiped["cart_items"] = CartItem.objects.all().delete()[0]
            wiped["carts"] = Cart.objects.all().delete()[0]
            wiped["favourites"] = Favourite.objects.all().delete()[0]
            wiped["pav_constructors"] = (
                ProductAttributeValueConstructor.objects.all().delete()[0]
            )
            wiped["media_constructors"] = (
                VariantMediaConstructor.objects.all().delete()[0]
            )
            wiped["char_constructors"] = (
                CharacteristicConstructor.objects.all().delete()[0]
            )
            wiped["stock_constructors"] = (
                VariantAttributeStockConstructor.objects.all().delete()[0]
            )
            wiped["variant_constructors"] = (
                VariantConstructor.objects.all().delete()[0]
            )
            wiped["product_constructors"] = (
                ProductConstructor.objects.all().delete()[0]
            )
            wiped["stocks"] = VariantAttributeStock.objects.all().delete()[0]
            wiped["pav"] = ProductAttributeValue.objects.all().delete()[0]
            wiped["characteristics"] = Characteristic.objects.all().delete()[0]
            wiped["medias"] = VariantMedia.objects.all().delete()[0]
            wiped["variants"] = Variant.objects.all().delete()[0]
            wiped["products"] = Product.objects.all().delete()[0]
            wiped["attribute_values"] = AttributeValue.objects.all().delete()[0]
            wiped["attributes"] = Attribute.objects.all().delete()[0]
            wiped["categories"] = Category.objects.all().delete()[0]
            wiped["units"] = Unit.objects.all().delete()[0]

            company = Company.objects.filter(status="active").first() or Company.objects.first()
            if company is None:
                raise RuntimeError("No Company found: seed at least one company first.")
            user = get_user_model().objects.order_by("id").first()

            unit_map = {}
            for en, ru, uz in UNITS:
                unit_map[en] = Unit.objects.create(unit=en, unit_ru=ru, unit_uz=uz)

            stats = {"roots": 0, "leafs": 0, "attrs": 0, "values": 0, "products": 0, "variants": 0}
            image_idx = 0
            view_seed = 0

            for root in ROOTS:
                root_en, root_ru, root_uz = root["n"]
                root_cat = Category.objects.create(
                    code=root["code"],
                    name=root_en,
                    name_en=root_en,
                    name_ru=root_ru,
                    name_uz=root_uz,
                    parent=None,
                    level=0,
                    is_leaf=False,
                    is_active=True,
                    image=CATEGORY_IMAGE_POOL[image_idx % len(CATEGORY_IMAGE_POOL)],
                )
                image_idx += 1
                stats["roots"] += 1

                for leaf in root["children"]:
                    leaf_en, leaf_ru, leaf_uz = leaf["n"]
                    leaf_cat = Category.objects.create(
                        code=leaf["code"],
                        name=leaf_en,
                        name_en=leaf_en,
                        name_ru=leaf_ru,
                        name_uz=leaf_uz,
                        parent=root_cat,
                        level=1,
                        is_leaf=True,
                        is_active=True,
                        image=CATEGORY_IMAGE_POOL[image_idx % len(CATEGORY_IMAGE_POOL)],
                    )
                    image_idx += 1
                    stats["leafs"] += 1

                    # Attributes + values for this leaf (drive storefront filters).
                    attr_map = {}  # attr_en -> (Attribute, {value_en: AttributeValue})
                    for attr_names, values in leaf["attrs"]:
                        attr_en, attr_ru, attr_uz = attr_names
                        attr = Attribute.objects.create(
                            name=attr_en,
                            name_en=attr_en,
                            name_ru=attr_ru,
                            name_uz=attr_uz,
                            attribute_type=Attribute.Type.SELECT,
                            category=leaf_cat,
                            is_filterable=True,
                        )
                        stats["attrs"] += 1
                        value_map = {}
                        for entry in values:
                            val_en, val_ru, val_uz = _t(entry)
                            value_map[val_en] = AttributeValue.objects.create(
                                attribute=attr,
                                value=val_en,
                                value_en=val_en,
                                value_ru=val_ru,
                                value_uz=val_uz,
                            )
                            stats["values"] += 1
                        attr_map[attr_en] = (attr, value_map)

                    for p_idx, product in enumerate(leaf["products"], start=1):
                        p_en, p_ru, p_uz = product["n"]
                        prices = [v["price"] for v in product["variants"]]
                        price_type = (
                            Product.PriceType.RANGE
                            if len(set(prices)) > 1
                            else Product.PriceType.EXACT
                        )
                        view_seed = (view_seed * 37 + 101) % 900
                        prod = Product.objects.create(
                            name=p_en,
                            name_en=p_en,
                            name_ru=p_ru,
                            name_uz=p_uz,
                            creator=None,
                            owner=company,
                            category=leaf_cat,
                            sku=f"BM-{leaf['code']}-{p_idx:03d}".upper(),
                            image=PRODUCT_IMAGE_POOL[
                                (stats["products"]) % len(PRODUCT_IMAGE_POOL)
                            ],
                            product_type=Product.ProductType.READY,
                            price_type=price_type,
                            price_min=Decimal(min(prices)),
                            price_max=Decimal(max(prices)),
                            is_active=True,
                            moq=product["moq"],
                            moq_unit=unit_map[product["unit"]],
                            lead_time_min=product["lead"][0],
                            lead_time_max=product["lead"][1],
                            average_rating=Decimal("4.5"),
                            view_count=100 + view_seed,
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
                                is_active=True,
                                average_rating=Decimal("4.5"),
                            )
                            stats["variants"] += 1

                            linked_values = []
                            for attr_en, val_en in variant["v"].items():
                                attr, value_map = attr_map[attr_en]
                                attr_value = value_map[val_en]
                                ProductAttributeValue.objects.create(
                                    product=var,
                                    attribute=attr,
                                    attribute_value=attr_value,
                                )
                                linked_values.append(attr_value)

                            stock = VariantAttributeStock.objects.create(
                                variant=var, quantity=variant["stock"]
                            )
                            if linked_values:
                                stock.attribute_values.add(*linked_values)

                            for char_name, char_value in product.get("chars", []):
                                Characteristic.objects.create(
                                    product_variant=var,
                                    name=char_name,
                                    value=char_value,
                                )

                            if user is not None:
                                VariantMedia.objects.create(
                                    user=user,
                                    product_variant=var,
                                    file=prod.image,
                                    product_media_type=VariantMedia.MediaType.PHOTO,
                                )

        self.stdout.write(self.style.SUCCESS(f"Wiped: {wiped}"))
        self.stdout.write(self.style.SUCCESS(f"Seeded: {stats}"))
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {stats['roots']} root / {stats['leafs']} leaf categories, "
                f"{stats['attrs']} attributes ({stats['values']} values), "
                f"{stats['products']} products, {stats['variants']} variants "
                f"for company '{company.name}'."
            )
        )
