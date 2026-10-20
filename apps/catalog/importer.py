import re
from collections import Counter

from django.db import transaction
from django.utils import timezone

from apps.catalog.models import (
    Attribute,
    Category,
    CategoryIcon,
    CategoryTableColumn,
    Product,
    ProductAttributeValue,
    StockStatus,
)
from apps.catalog.utils import normalize_search, normalize_value, value_rank

SLUG_RE = re.compile(r"^[-a-zA-Z0-9_]+$")
BATCH_SIZE = 500
MAX_ERRORS = 20
PRODUCT_FIELDS = (
    "name",
    "category_id",
    "price",
    "pack",
    "stock",
    "is_featured",
    "is_active",
    "search_text",
)


class CatalogImportError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("\n".join(errors))


def chunks(items, size=BATCH_SIZE):
    items = list(items)
    for start in range(0, len(items), size):
        yield items[start : start + size]


class CatalogImporter:
    """Loads the frontend catalog export (tools/export_catalog.mts) into the database.

    Qayta ishga tushirsa bo'ladi: yozuvlar kalit, yo'l va artikul bo'yicha
    yangilanadi. Mahsulotning xususiyat qiymatlari fayldagi holatga keltiriladi.
    """

    def __init__(self, data, deactivate_missing=False):
        self.data = data
        self.deactivate_missing = deactivate_missing
        self.stats = Counter()
        self.attributes = {}
        self.categories = {}

    def run(self, dry_run=False):
        self.validate()
        with transaction.atomic():
            self.import_attributes()
            self.import_categories()
            self.import_products()
            if dry_run:
                transaction.set_rollback(True)
        return self.stats

    # ------------------------------------------------------------ validation

    def validate(self):
        errors = []
        data = self.data

        for section in ("attributes", "categories", "products"):
            if not isinstance(data.get(section), list):
                raise CatalogImportError([f"Faylda `{section}` ro'yxati yo'q"])

        attribute_keys = [attribute.get("key") for attribute in data["attributes"]]
        known_keys = set(attribute_keys)
        for key, count in Counter(attribute_keys).items():
            if count > 1:
                errors.append(f"Xususiyat kaliti takrorlangan: {key}")
            if not key or not SLUG_RE.match(key):
                errors.append(f"Xususiyat kaliti noto'g'ri: {key!r}")
        for attribute in data["attributes"]:
            requires = attribute.get("requires")
            if requires and requires.get("key") not in known_keys:
                errors.append(
                    f"{attribute['key']}: shartdagi xususiyat topilmadi: {requires.get('key')}"
                )

        paths = [tuple(category.get("path") or ()) for category in data["categories"]]
        known_paths = set(paths)
        parent_paths = {path[:-1] for path in paths}
        icons = set(CategoryIcon.values)
        for path, count in Counter(paths).items():
            if count > 1:
                errors.append(f"Kategoriya takrorlangan: {'/'.join(path)}")
        for category, path in zip(data["categories"], paths, strict=False):
            label = "/".join(path) or "?"
            if not path or not all(SLUG_RE.match(slug or "") for slug in path):
                errors.append(f"Kategoriya yo'li noto'g'ri: {label}")
            elif len(path) > 1 and path[:-1] not in known_paths:
                errors.append(f"{label}: yuqori kategoriya topilmadi")
            if category.get("icon") not in icons:
                errors.append(f"{label}: noma'lum ikonka {category.get('icon')!r}")
            table = category.get("table") or {}
            for key in [table.get("group_by"), *table.get("columns", [])]:
                if key and key not in known_keys:
                    errors.append(f"{label}: jadvaldagi xususiyat topilmadi: {key}")

        skus = Counter(product.get("sku") for product in data["products"])
        for sku, count in skus.items():
            if count > 1:
                errors.append(f"Artikul takrorlangan: {sku}")
        stocks = set(StockStatus.values)
        for product in data["products"]:
            sku = product.get("sku") or "?"
            path = tuple(product.get("path") or ())
            if not product.get("sku") or not product.get("name"):
                errors.append(f"{sku}: artikul yoki nomi bo'sh")
            if path not in known_paths or path in parent_paths:
                errors.append(
                    f"{sku}: kategoriya oxirgi darajada emas yoki topilmadi: {'/'.join(path)}"
                )
            if not isinstance(product.get("price"), int) or product["price"] < 0:
                errors.append(f"{sku}: narx butun musbat son bo'lishi kerak")
            if not isinstance(product.get("pack"), int) or product["pack"] < 1:
                errors.append(f"{sku}: qadoqdagi soni kamida 1 bo'lishi kerak")
            if product.get("stock") not in stocks:
                errors.append(f"{sku}: noma'lum holat {product.get('stock')!r}")
            for key in product.get("attrs") or {}:
                if key not in known_keys:
                    errors.append(f"{sku}: noma'lum xususiyat {key}")

        for sku in data.get("featured") or []:
            if sku not in skus:
                errors.append(f"Ommabop ro'yxatidagi artikul topilmadi: {sku}")

        if errors:
            if len(errors) > MAX_ERRORS:
                errors = errors[:MAX_ERRORS] + [f"... yana {len(errors) - MAX_ERRORS} ta xato"]
            raise CatalogImportError(errors)

    # ------------------------------------------------------------ attributes

    def import_attributes(self):
        existing = {attribute.key: attribute for attribute in Attribute.objects.all()}

        for row in self.data["attributes"]:
            attribute = existing.get(row["key"]) or Attribute(key=row["key"])
            self.stats["attributes_created" if attribute.pk is None else "attributes_updated"] += 1
            attribute.label = row["label"]
            attribute.order = row.get("order", 0)
            attribute.save()
            self.attributes[attribute.key] = attribute

        for row in self.data["attributes"]:
            attribute = self.attributes[row["key"]]
            requires = row.get("requires") or {}
            attribute.requires_attribute = self.attributes.get(requires.get("key"))
            attribute.requires_value = (
                requires.get("value", "") if attribute.requires_attribute else ""
            )
            attribute.save(update_fields=["requires_attribute", "requires_value", "modified_at"])

    # ------------------------------------------------------------ categories

    def import_categories(self):
        existing = {}
        nodes = {category.pk: category for category in Category.objects.all()}
        for category in nodes.values():
            path = []
            current = category
            while current is not None:
                path.append(current.slug)
                current = nodes.get(current.parent_id)
            existing[tuple(reversed(path))] = category

        rows = sorted(self.data["categories"], key=lambda row: len(row["path"]))
        for row in rows:
            path = tuple(row["path"])
            category = existing.get(path) or Category(
                slug=path[-1], parent=self.categories.get(path[:-1])
            )
            self.stats["categories_created" if category.pk is None else "categories_updated"] += 1
            table = row.get("table") or {}
            category.name = row["name"]
            category.icon = row["icon"]
            category.description = row.get("description") or ""
            category.order = row.get("order", 0)
            category.table_group_by = self.attributes.get(table.get("group_by"))
            category.save()
            self.categories[path] = category
            self.sync_table_columns(category, table.get("columns", []))

    def sync_table_columns(self, category, keys):
        columns = {column.attribute_id: column for column in category.table_columns.all()}
        wanted = [self.attributes[key] for key in keys]
        wanted_ids = {attribute.pk for attribute in wanted}

        stale = [
            column.pk for attribute_id, column in columns.items() if attribute_id not in wanted_ids
        ]
        if stale:
            CategoryTableColumn.objects.filter(pk__in=stale).delete()

        for order, attribute in enumerate(wanted):
            column = columns.get(attribute.pk) or CategoryTableColumn(
                category=category, attribute=attribute
            )
            if column.pk is None or column.order != order:
                column.order = order
                column.save()

    # -------------------------------------------------------------- products

    def import_products(self):
        rows = self.data["products"]
        featured = set(self.data.get("featured") or [])
        existing = {product.sku: product for product in Product.objects.all()}
        now = timezone.now()
        to_create, to_update = [], []

        for row in rows:
            product = existing.get(row["sku"]) or Product(sku=row["sku"])
            fields = {
                "name": row["name"],
                "category_id": self.categories[tuple(row["path"])].pk,
                "price": row["price"],
                "pack": row["pack"],
                "stock": row["stock"],
                "is_featured": row["sku"] in featured,
                "is_active": True,
                # bulk_* `save()` ni chaqirmaydi: hisoblanadigan maydon shu yerda to'ldiriladi.
                "search_text": normalize_search(f"{row['name']} {row['sku']}"),
            }
            if product.pk is not None and all(
                getattr(product, name) == value for name, value in fields.items()
            ):
                continue
            for name, value in fields.items():
                setattr(product, name, value)
            if product.pk is None:
                to_create.append(product)
            else:
                product.modified_at = now
                to_update.append(product)

        Product.objects.bulk_create(to_create, batch_size=BATCH_SIZE)
        Product.objects.bulk_update(
            to_update, [*PRODUCT_FIELDS, "modified_at"], batch_size=BATCH_SIZE
        )
        self.stats["products_created"] = len(to_create)
        self.stats["products_updated"] = len(to_update)
        self.stats["products_unchanged"] = len(rows) - len(to_create) - len(to_update)

        product_ids = dict(Product.objects.values_list("sku", "id"))
        self.import_values(rows, product_ids, now)

        if self.deactivate_missing:
            imported = {row["sku"] for row in rows}
            missing = [pk for sku, pk in product_ids.items() if sku not in imported]
            for batch in chunks(missing):
                self.stats["products_deactivated"] += Product.objects.filter(
                    pk__in=batch, is_active=True
                ).update(is_active=False, modified_at=now)

    def import_values(self, rows, product_ids, now):
        """Bring attribute values of the imported products to the file state."""
        imported_ids = {product_ids[row["sku"]] for row in rows}
        existing = {}
        for batch in chunks(imported_ids):
            for value in ProductAttributeValue.objects.filter(product_id__in=batch).only(
                "id", "product_id", "attribute_id", "value"
            ):
                existing[(value.product_id, value.attribute_id)] = value

        to_create, to_update, seen = [], [], set()
        for row in rows:
            product_id = product_ids[row["sku"]]
            for key, raw_value in (row.get("attrs") or {}).items():
                attribute_id = self.attributes[key].pk
                seen.add((product_id, attribute_id))
                value = normalize_value(raw_value)
                current = existing.get((product_id, attribute_id))
                if current is not None and current.value == value:
                    continue
                sort_group, sort_number = value_rank(value)
                if current is None:
                    to_create.append(
                        ProductAttributeValue(
                            product_id=product_id,
                            attribute_id=attribute_id,
                            value=value,
                            sort_group=sort_group,
                            sort_number=sort_number,
                        )
                    )
                else:
                    current.value = value
                    current.sort_group, current.sort_number = sort_group, sort_number
                    current.modified_at = now
                    to_update.append(current)

        stale = [value.pk for key, value in existing.items() if key not in seen]
        for batch in chunks(stale):
            ProductAttributeValue.objects.filter(pk__in=batch).delete()
        ProductAttributeValue.objects.bulk_create(to_create, batch_size=BATCH_SIZE)
        ProductAttributeValue.objects.bulk_update(
            to_update,
            ["value", "sort_group", "sort_number", "modified_at"],
            batch_size=BATCH_SIZE,
        )
        self.stats["values_created"] = len(to_create)
        self.stats["values_updated"] = len(to_update)
        self.stats["values_deleted"] = len(stale)
