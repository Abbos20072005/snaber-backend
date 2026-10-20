"""Catalog browsing rules ported from the frontend `lib/catalog/engine.ts`.

Kategoriya mahsulotlari va ularning xususiyat qiymatlari bir marta yuklanadi,
filtr, sanash va tartib esa Python da frontenddagi bilan aynan bir xil
qilinadi. Eng katta tarmoq ham bir necha o'n ming qator: bu SQL dagi
subquery'lardan tez va har ikkala bazada bir xil natija beradi.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache

from apps.catalog.models import Category, Product, ProductAttributeValue, StockStatus
from apps.catalog.utils import value_rank

VARIANT_LIMIT = 10
LENGTH_KEY = "length"


@dataclass
class CatalogQuery:
    """Parsed browse request: category, attribute selection and search terms."""

    category: Category | None = None
    selection: dict = field(default_factory=dict)
    terms: list = field(default_factory=list)


# ICU (JS `localeCompare`) tinish belgilarini harf va raqamlardan oldin, o'z
# tartibida qo'yadi: masalan "1/2-13" < '1/2"', kod nuqtasi bo'yicha esa aksincha.
ICU_PUNCTUATION = " _-,;:!?.'\"()[]{}@*/\\&#%`^+<=>|~$"
_TEXT_TRANSLATION = str.maketrans(
    {char: chr(1 + index) for index, char in enumerate(ICU_PUNCTUATION)} | {"ё": "е"}
)


def text_key(value):
    """Approximates JS `localeCompare`: punctuation first, case-insensitive, lowercase before uppercase."""
    return value.casefold().translate(_TEXT_TRANSLATION), value.swapcase()


@lru_cache(maxsize=50_000)
def compare_key(value):
    """Frontend `compareValues`: inch before metric, by real size, then as text."""
    group, number = value_rank(value)
    return group, float("inf") if number is None else number, text_key(value)


@dataclass
class ProductRow:
    id: int
    sku: str
    name: str
    category_id: int
    price: int
    pack: int
    stock: str
    attrs: dict


class CategoryPool:
    """Active products of a category branch with their attribute values (keyed by attribute key)."""

    def __init__(self, tree, category):
        products = Product.objects.filter(is_active=True)
        if category is not None:
            products = products.filter(category_id__in=tree.get_descendant_ids(category.pk))
        self.queryset = products
        self.rows = [
            ProductRow(*fields, attrs={})
            for fields in products.order_by("id").values_list(
                "id", "sku", "name", "category_id", "price", "pack", "stock"
            )
        ]
        by_id = {row.id: row for row in self.rows}
        values = (
            ProductAttributeValue.objects.filter(product__in=products)
            .order_by("attribute__order", "attribute_id")
            .values_list("product_id", "attribute__key", "value")
        )
        for product_id, key, value in values:
            by_id[product_id].attrs[key] = value

    def search_ids(self, terms):
        """Ids matching every search term, or None when there is no search."""
        if not terms:
            return None
        products = self.queryset
        for term in terms:
            products = products.filter(search_text__contains=term)
        return set(products.values_list("id", flat=True))

    def failed_keys(self, row, selection):
        return [key for key, values in selection.items() if row.attrs.get(key) not in values]

    def matching(self, query):
        """Rows passing every filter and the search, in catalog order."""
        found = self.search_ids(query.terms)
        return [
            row
            for row in self.rows
            if (found is None or row.id in found) and not self.failed_keys(row, query.selection)
        ]


def order_rows(rows, group_key=None):
    """Table order: group attribute, then length, then name; otherwise catalog order."""
    if group_key is None:
        return list(rows)
    return sorted(
        rows,
        key=lambda row: (
            compare_key(row.attrs.get(group_key, "")),
            compare_key(row.attrs.get(LENGTH_KEY, "")),
            text_key(row.name),
        ),
    )


def first_available(rows):
    """Where a leaf category opens: the first product that is not made to order."""
    return next((row for row in rows if row.stock != StockStatus.ON_ORDER), rows[0] if rows else None)


def group_key_of(tree, category):
    if category is None or not tree.is_leaf(category.pk) or category.table_group_by is None:
        return None
    return category.table_group_by.key


def build_facets(pool, query, attributes):
    """McMaster-style filters.

    Xususiyat faqat mahsulotlarni hali ajratib turgan bo'lsa chiqadi; uning
    qiymatlari BOSHQA barcha filtrlardan o'tgan mahsulotlar bo'yicha sanaladi.
    Shuning uchun "Метрическая" tanlansa rezba ro'yxati o'zi metrikga almashadi.
    """
    found = pool.search_ids(query.terms)
    present = set()
    counts = defaultdict(Counter)
    for row in pool.rows:
        present.update(row.attrs)
        if found is not None and row.id not in found:
            continue
        failed = pool.failed_keys(row, query.selection)
        if len(failed) > 1:
            continue
        for key, value in row.attrs.items():
            if not failed or failed[0] == key:
                counts[key][value] += 1

    facets = []
    for attribute in attributes:
        if attribute.key not in present:
            continue
        requirement = attribute.requires_attribute
        if requirement is not None and attribute.requires_value not in query.selection.get(
            requirement.key, []
        ):
            continue

        options = dict(counts.get(attribute.key, {}))
        chosen = query.selection.get(attribute.key, [])
        for value in chosen:
            options.setdefault(value, 0)
        if len(options) < 2 and not chosen:
            continue

        facets.append(
            {
                "key": attribute.key,
                "label": attribute.label,
                "options": [
                    {"value": value, "count": options[value], "selected": value in chosen}
                    for value in sorted(options, key=compare_key)
                ],
            }
        )
    return facets


def count_by_child(tree, category, rows):
    """Matching products per child category (category cards)."""
    per_category = Counter(row.category_id for row in rows)
    children = []
    for child in tree.get_children(category.pk if category else None):
        count = sum(per_category[pk] for pk in tree.get_descendant_ids(child.pk))
        if count:
            children.append({"category": child, "count": count})
    return children


def build_variants(product, family, attributes, limit=VARIANT_LIMIT):
    """Chip rows of the product card; `family` is the product's leaf pool rows.

    Kategoriya ichida o'zgaradigan har bir xususiyat bir qator bo'ladi; chip
    shu qiymatli va boshqa tanlovlarni iloji boricha saqlaydigan variantga
    olib boradi, teng bo'lsa arzoniga.
    """
    own = next(row for row in family if row.id == product.pk).attrs

    # Bog'liq xususiyat (qadam rezbadan kelib chiqadi) alohida qator bo'lmaydi.
    varying = [
        attribute.key
        for attribute in attributes
        if attribute.requires_attribute_id is None
        and attribute.key in own
        and len({row.attrs.get(attribute.key) for row in family} - {None}) > 1
    ][:limit]
    labels = {attribute.key: attribute.label for attribute in attributes}

    groups = []
    for key in varying:
        members = defaultdict(list)
        for row in family:
            if key in row.attrs:
                members[row.attrs[key]].append(row)

        options = []
        for value in sorted(members, key=compare_key):
            best, best_score = None, -1
            for row in members[value]:
                score = sum(1 for other in varying if other != key and row.attrs.get(other) == own.get(other))
                if score > best_score or (score == best_score and row.price < best.price):
                    best, best_score = row, score
            options.append({"value": value, "sku": best.sku, "selected": own[key] == value})

        groups.append({"key": key, "label": labels[key], "value": own[key], "options": options})
    return groups


def related_ids(product, family, limit):
    """Same leaf, not made to order; most shared attribute values first, then cheaper."""
    own = next(row for row in family if row.id == product.pk).attrs
    candidates = [
        row for row in family if row.id != product.pk and row.stock != StockStatus.ON_ORDER
    ]

    def shared(row):
        return sum(1 for key, value in own.items() if row.attrs.get(key) == value)

    ranked = sorted(candidates, key=lambda row: (-shared(row), row.price))
    return [row.id for row in ranked[:limit]]
