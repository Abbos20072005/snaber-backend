"""Small catalog in the `tools/export_catalog.mts` format, shared by the tests."""

BOLTS = ["consumables", "fasteners", "bolts"]
NUTS = ["consumables", "fasteners", "nuts"]
CABLE = ["consumables", "electrical", "cable"]

METRIC = "Метрическая"
INCH = "Дюймовая"

CATALOG = {
    "attributes": [
        {"key": "system", "label": "Система мер", "order": 0, "requires": None},
        {"key": "thread", "label": "Размер резьбы", "order": 1, "requires": None},
        {
            "key": "pitch",
            "label": "Шаг резьбы",
            "order": 2,
            "requires": {"key": "system", "value": METRIC},
        },
        {"key": "length", "label": "Длина", "order": 3, "requires": None},
        {"key": "cores", "label": "Количество жил", "order": 4, "requires": None},
        {"key": "material", "label": "Материал", "order": 5, "requires": None},
    ],
    "categories": [
        {"path": ["consumables"], "name": "Расходники", "icon": "fasteners", "description": "", "order": 0, "table": None},
        {"path": ["consumables", "fasteners"], "name": "Крепёж", "icon": "screws", "description": "", "order": 0, "table": None},
        {
            "path": BOLTS,
            "name": "Болты",
            "icon": "screws",
            "description": "Болты и винты",
            "order": 0,
            "table": {"group_by": "thread", "columns": ["length", "material"]},
        },
        {
            "path": NUTS,
            "name": "Гайки",
            "icon": "nuts",
            "description": "",
            "order": 1,
            "table": {"group_by": "thread", "columns": ["material"]},
        },
        {"path": ["consumables", "electrical"], "name": "Электрика", "icon": "electrical", "description": "", "order": 1, "table": None},
        {
            "path": CABLE,
            "name": "Кабель",
            "icon": "cable",
            "description": "",
            "order": 0,
            "table": {"group_by": "cores", "columns": ["material"]},
        },
    ],
    "products": [
        {
            "sku": "B-1",
            "name": "Болт M10 x 20 мм",
            "path": BOLTS,
            "price": 300,
            "pack": 25,
            "stock": "in-stock",
            "attrs": {"system": METRIC, "thread": "M10", "pitch": "1.5 мм", "length": "20 мм", "material": "Сталь"},
        },
        {
            "sku": "B-2",
            "name": "Болт M6 x 20 мм",
            "path": BOLTS,
            "price": 100,
            "pack": 50,
            "stock": "on-order",
            "attrs": {"system": METRIC, "thread": "M6", "pitch": "1 мм", "length": "20 мм", "material": "Сталь"},
        },
        {
            "sku": "B-3",
            "name": "Болт M6 x 10 мм",
            "path": BOLTS,
            "price": 200,
            "pack": 50,
            "stock": "in-stock",
            "attrs": {"system": METRIC, "thread": "M6", "pitch": "1 мм", "length": "10 мм", "material": "Нержавеющая сталь"},
        },
        {
            "sku": "B-4",
            "name": "Болт #10-24 x 1\"",
            "path": BOLTS,
            "price": 150,
            "pack": 100,
            "stock": "low",
            "attrs": {"system": INCH, "thread": "#10-24", "length": "1\"", "material": "Сталь"},
        },
        {
            "sku": "N-1",
            "name": "Гайка M6",
            "path": NUTS,
            "price": 50,
            "pack": 100,
            "stock": "in-stock",
            "attrs": {"system": METRIC, "thread": "M6", "material": "Сталь"},
        },
        {
            "sku": "C-1",
            "name": "Кабель ВВГ 3x2.5",
            "path": CABLE,
            "price": 9000,
            "pack": 1,
            "stock": "in-stock",
            "attrs": {"cores": "3", "material": "Медь"},
        },
    ],
    "featured": ["B-4"],
}
