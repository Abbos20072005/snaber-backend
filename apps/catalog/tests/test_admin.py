import pytest
from django.urls import reverse

from apps.catalog.models import Attribute, Category, Product, ProductAttributeValue


@pytest.fixture
def catalog():
    root = Category.objects.create(slug="consumables", name="Расходники")
    fasteners = Category.objects.create(parent=root, slug="fasteners", name="Крепёж")
    bolts = Category.objects.create(parent=fasteners, slug="bolts", name="Болты")
    product = Product.objects.create(sku="B-1", name="Болт M6", category=bolts, price=1000)
    return {"root": root, "fasteners": fasteners, "bolts": bolts, "product": product}


@pytest.mark.django_db
class TestCategoryAdmin:
    def test_changelist_shows_tree_and_counts(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:catalog_category_changelist"))

        content = response.content.decode()
        assert response.status_code == 200
        assert content.index("Расходники") < content.index("Крепёж") < content.index("Болты")
        assert "+ ichki kategoriya" in content

    def test_parent_choices_skip_categories_with_products(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:catalog_category_add"))

        choices = dict(response.context["adminform"].form.fields["parent"].choices)
        labels = [str(label) for label in choices.values()]
        assert "Расходники › Крепёж" in labels
        assert "Расходники › Крепёж › Болты" not in labels

    def test_add_child_to_category_with_products_is_rejected(self, admin_client, catalog):
        response = admin_client.post(
            reverse("admin:catalog_category_add"),
            {
                "parent": catalog["bolts"].pk,
                "name": "Длинные",
                "slug": "long",
                "icon": "screws",
                "order": 0,
                "table_columns-TOTAL_FORMS": 0,
                "table_columns-INITIAL_FORMS": 0,
            },
        )

        assert response.status_code == 200
        assert not Category.objects.filter(slug="long").exists()


@pytest.mark.django_db
class TestProductAdmin:
    def test_changelist_shows_category_path(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:catalog_product_changelist"))

        assert response.status_code == 200
        assert "Расходники › Крепёж › Болты" in response.content.decode()

    def test_search_finds_cyrillic_in_other_case(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:catalog_product_changelist"), {"q": "БОЛТ"})

        assert list(response.context["cl"].result_list) == [catalog["product"]]

    def test_category_filter_includes_subcategories(self, admin_client, catalog):
        response = admin_client.get(
            reverse("admin:catalog_product_changelist"), {"category": catalog["root"].pk}
        )

        assert list(response.context["cl"].result_list) == [catalog["product"]]

    def test_create_product_with_attribute_sets_author(self, admin_client, admin_user, catalog):
        attribute = Attribute.objects.create(key="thread", label="Размер резьбы")

        response = admin_client.post(
            reverse("admin:catalog_product_add"),
            {
                "sku": "B-2",
                "name": "Болт M8",
                "category": catalog["bolts"].pk,
                "price": 1200,
                "pack": 50,
                "stock": "low",
                "is_active": "on",
                "attribute_values-TOTAL_FORMS": 1,
                "attribute_values-INITIAL_FORMS": 0,
                "attribute_values-0-attribute": attribute.pk,
                "attribute_values-0-value": "M8",
            },
        )

        assert response.status_code == 302
        product = Product.objects.get(sku="B-2")
        assert product.created_by == admin_user
        value = ProductAttributeValue.objects.get(product=product)
        assert (value.value, value.created_by) == ("M8", admin_user)

    def test_category_choices_are_leaves_only(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:catalog_product_add"))

        labels = [str(label) for _, label in response.context["adminform"].form.fields["category"].choices]
        assert "Расходники › Крепёж › Болты" in labels
        assert "Расходники › Крепёж" not in labels
