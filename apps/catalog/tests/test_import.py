import copy
import io
import json

import pytest
from django.core.management import CommandError, call_command

from apps.catalog.models import Attribute, Category, Product, ProductAttributeValue

CATALOG = {
    "attributes": [
        {"key": "system", "label": "Система мер", "order": 0, "requires": None},
        {"key": "thread", "label": "Размер резьбы", "order": 1, "requires": None},
        {
            "key": "pitch",
            "label": "Шаг резьбы",
            "order": 2,
            "requires": {"key": "system", "value": "Метрическая"},
        },
    ],
    "categories": [
        {
            "path": ["consumables"],
            "name": "Расходники",
            "icon": "fasteners",
            "description": "",
            "order": 0,
            "table": None,
        },
        {
            "path": ["consumables", "fasteners"],
            "name": "Крепёж",
            "icon": "screws",
            "description": "",
            "order": 0,
            "table": None,
        },
        {
            "path": ["consumables", "fasteners", "bolts"],
            "name": "Болты",
            "icon": "screws",
            "description": "Болты и винты",
            "order": 0,
            "table": {"group_by": "thread", "columns": ["system", "pitch"]},
        },
    ],
    "products": [
        {
            "sku": "SHA-00001",
            "name": "Винт M6",
            "path": ["consumables", "fasteners", "bolts"],
            "price": 12000,
            "pack": 50,
            "stock": "in-stock",
            "attrs": {"system": "Метрическая", "thread": "M6", "pitch": "1 мм"},
        },
        {
            "sku": "SHA-00002",
            "name": "Винт #10-24",
            "path": ["consumables", "fasteners", "bolts"],
            "price": 15000,
            "pack": 100,
            "stock": "low",
            "attrs": {"system": "Дюймовая", "thread": "#10-24"},
        },
    ],
    "featured": ["SHA-00002"],
}


@pytest.fixture
def write_catalog(tmp_path):
    def write(data):
        path = tmp_path / "catalog.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return str(path)

    return write


@pytest.mark.django_db
class TestImportCatalog:
    def test_import_creates_tree_products_and_values(self, write_catalog):
        call_command("import_catalog", write_catalog(CATALOG), stdout=None)

        bolts = Category.objects.get(slug="bolts")
        assert bolts.parent.slug == "fasteners"
        assert bolts.table_group_by.key == "thread"
        assert [column.attribute.key for column in bolts.table_columns.all()] == ["system", "pitch"]
        pitch = Attribute.objects.get(key="pitch")
        assert (pitch.requires_attribute.key, pitch.requires_value) == ("system", "Метрическая")
        product = Product.objects.get(sku="SHA-00002")
        assert (product.price, product.pack, product.stock, product.is_featured) == (
            15000,
            100,
            "low",
            True,
        )
        assert product.search_text == "винт #10-24 sha-00002"
        value = ProductAttributeValue.objects.get(product=product, attribute__key="thread")
        assert (value.sort_group, round(value.sort_number, 3)) == (0, 0.19)

    def test_reimport_updates_without_duplicates(self, write_catalog):
        call_command("import_catalog", write_catalog(CATALOG))
        changed = copy.deepcopy(CATALOG)
        changed["products"][0]["name"] = "Винт M6 x 20"
        del changed["products"][0]["attrs"]["pitch"]
        changed["categories"][2]["table"]["columns"] = ["pitch"]

        call_command("import_catalog", write_catalog(changed))

        assert Category.objects.count() == 3
        assert Product.objects.count() == 2
        product = Product.objects.get(sku="SHA-00001")
        assert product.name == "Винт M6 x 20"
        assert product.search_text.startswith("винт m6 x 20")
        assert not product.attribute_values.filter(attribute__key="pitch").exists()
        assert list(
            Category.objects.get(slug="bolts").table_columns.values_list(
                "attribute__key", flat=True
            )
        ) == ["pitch"]

    def test_reimport_of_same_file_skips_unchanged_rows(self, write_catalog):
        path = write_catalog(CATALOG)
        call_command("import_catalog", path)
        output = io.StringIO()

        call_command("import_catalog", path, stdout=output)

        report = output.getvalue()
        assert "products_unchanged: 2" in report
        assert "products_updated: 0" in report
        assert "values_created: 0" in report

    def test_deactivate_missing_hides_products_not_in_file(self, write_catalog):
        call_command("import_catalog", write_catalog(CATALOG))
        shorter = copy.deepcopy(CATALOG)
        shorter["products"] = shorter["products"][:1]
        shorter["featured"] = []

        call_command("import_catalog", write_catalog(shorter), deactivate_missing=True)

        assert list(Product.objects.filter(is_active=True).values_list("sku", flat=True)) == [
            "SHA-00001"
        ]

    def test_dry_run_writes_nothing(self, write_catalog):
        call_command("import_catalog", write_catalog(CATALOG), dry_run=True)

        assert not Product.objects.exists()
        assert not Category.objects.exists()

    def test_unknown_attribute_aborts_import(self, write_catalog):
        broken = copy.deepcopy(CATALOG)
        broken["products"][0]["attrs"]["color"] = "Белый"

        with pytest.raises(CommandError, match="noma'lum xususiyat color"):
            call_command("import_catalog", write_catalog(broken))

        assert not Product.objects.exists()

    def test_product_in_non_leaf_category_aborts_import(self, write_catalog):
        broken = copy.deepcopy(CATALOG)
        broken["products"][0]["path"] = ["consumables", "fasteners"]

        with pytest.raises(CommandError, match="SHA-00001: kategoriya oxirgi darajada emas"):
            call_command("import_catalog", write_catalog(broken))

    def test_missing_file_raises_command_error(self, tmp_path):
        with pytest.raises(CommandError, match="Fayl topilmadi"):
            call_command("import_catalog", str(tmp_path / "missing.json"))
