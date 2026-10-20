import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.catalog.models import (
    Attribute,
    Category,
    Product,
    ProductAttributeValue,
    StockStatus,
)
from apps.catalog.services import CategoryTree
from apps.catalog.utils import value_rank


def sort_key(value):
    group, number = value_rank(value)
    return group, float("inf") if number is None else number, value


@pytest.fixture
def tree_data():
    root = Category.objects.create(slug="consumables", name="Расходники", order=1)
    fasteners = Category.objects.create(parent=root, slug="fasteners", name="Крепёж")
    bolts = Category.objects.create(parent=fasteners, slug="bolts", name="Болты", order=2)
    nuts = Category.objects.create(parent=fasteners, slug="nuts", name="Гайки", order=1)
    Product.objects.create(sku="B-1", name="Болт M6", category=bolts, price=1000)
    Product.objects.create(sku="B-2", name="Болт M8", category=bolts, price=1200)
    Product.objects.create(sku="N-1", name="Гайка M6", category=nuts, price=500, is_active=False)
    return {"root": root, "fasteners": fasteners, "bolts": bolts, "nuts": nuts}


class TestValueRank:
    def test_inch_values_sort_by_real_size_before_metric(self):
        values = ["M10", "1/4-20", "6 мм", "#10-24", "M6", '1/2"', "#4-40", '1-1/4"']

        ordered = sorted(values, key=sort_key)

        assert ordered == ["#4-40", "#10-24", "1/4-20", '1/2"', '1-1/4"', "6 мм", "M6", "M10"]

    def test_value_without_number_goes_last(self):
        assert value_rank("Сталь") == (0, None)


@pytest.mark.django_db
class TestProductAttributeValue:
    def test_save_normalizes_spaces_and_fills_sort_fields(self, tree_data):
        attribute = Attribute.objects.create(key="thread", label="Размер резьбы")
        product = Product.objects.get(sku="B-1")

        value = ProductAttributeValue.objects.create(
            product=product, attribute=attribute, value="  M10   "
        )

        assert value.value == "M10"
        assert (value.sort_group, value.sort_number) == (1, 10.0)

    def test_same_attribute_twice_raises_integrity_error(self, tree_data):
        attribute = Attribute.objects.create(key="thread", label="Размер резьбы")
        product = Product.objects.get(sku="B-1")
        ProductAttributeValue.objects.create(product=product, attribute=attribute, value="M6")

        with pytest.raises(IntegrityError), transaction.atomic():
            ProductAttributeValue.objects.create(product=product, attribute=attribute, value="M8")


@pytest.mark.django_db
class TestProduct:
    def test_search_text_matches_cyrillic_in_any_case(self, tree_data):
        found = Product.objects.filter(search_text__contains="болт m6")

        assert list(found.values_list("sku", flat=True)) == ["B-1"]

    def test_search_text_includes_sku(self, tree_data):
        assert Product.objects.get(sku="B-2").search_text == "болт m8 b-2"

    def test_clean_rejects_category_with_children(self, tree_data):
        product = Product(sku="X-1", name="Болт", category=tree_data["fasteners"], price=100)

        with pytest.raises(ValidationError) as error:
            product.full_clean()

        assert "category" in error.value.message_dict

    def test_default_stock_is_in_stock(self, tree_data):
        assert Product.objects.get(sku="B-1").stock == StockStatus.IN_STOCK


@pytest.mark.django_db
class TestCategory:
    def test_same_slug_allowed_under_different_parents(self, tree_data):
        Category.objects.create(parent=tree_data["root"], slug="bolts", name="Болты 2")

        assert Category.objects.filter(slug="bolts").count() == 2

    def test_duplicate_root_slug_raises_integrity_error(self, tree_data):
        with pytest.raises(IntegrityError), transaction.atomic():
            Category.objects.create(slug="consumables", name="Дубль")

    def test_clean_rejects_moving_into_own_descendant(self, tree_data):
        root = tree_data["root"]
        root.parent = tree_data["fasteners"]

        with pytest.raises(ValidationError) as error:
            root.full_clean()

        assert "parent" in error.value.message_dict

    def test_clean_rejects_parent_with_products(self, tree_data):
        child = Category(parent=tree_data["bolts"], slug="long", name="Длинные")

        with pytest.raises(ValidationError) as error:
            child.full_clean()

        assert "parent" in error.value.message_dict


@pytest.mark.django_db
class TestAttribute:
    def test_clean_requires_value_for_condition(self):
        system = Attribute.objects.create(key="system", label="Система мер")
        pitch = Attribute(key="pitch", label="Шаг резьбы", requires_attribute=system)

        with pytest.raises(ValidationError) as error:
            pitch.full_clean()

        assert "requires_value" in error.value.message_dict


@pytest.mark.django_db
class TestCategoryTree:
    def test_walk_follows_order_inside_parent(self, tree_data):
        tree = CategoryTree.load()

        names = [category.slug for category, _ in tree.walk()]

        assert names == ["consumables", "fasteners", "nuts", "bolts"]

    def test_branch_count_skips_inactive_products(self, tree_data):
        tree = CategoryTree.load()

        assert tree.get_branch_count(tree_data["root"].pk) == 2
        assert tree.get_branch_count(tree_data["nuts"].pk) == 0

    def test_label_is_full_path(self, tree_data):
        tree = CategoryTree.load()

        assert tree.get_label(tree_data["bolts"].pk) == "Расходники › Крепёж › Болты"
