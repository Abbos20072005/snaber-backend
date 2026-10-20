import pytest
from django.urls import reverse
from rest_framework import status

from apps.catalog.models import Product
from apps.catalog.tests.fixtures import INCH, METRIC

BOLTS = "consumables/fasteners/bolts"


def skus(results):
    return [product["sku"] for product in results]


def facet(body, key):
    found = next((item for item in body["facets"] if item["key"] == key), None)
    if found is None:
        return None
    return [(option["value"], option["count"], option["selected"]) for option in found["options"]]


@pytest.mark.django_db
class TestCatalogTreeAPI:
    def test_tree_returns_nested_categories_with_counts(self, api_client, catalog):
        response = api_client.get(reverse("catalog-tree"))

        assert response.status_code == status.HTTP_200_OK
        (root,) = response.data
        assert (root["slug"], root["product_count"]) == ("consumables", 6)
        assert [(child["slug"], child["product_count"]) for child in root["children"]] == [
            ("fasteners", 5),
            ("electrical", 1),
        ]
        bolts = root["children"][0]["children"][0]
        assert bolts["table"] == {"group_by": "thread", "columns": ["length", "material"]}
        assert bolts["children"] == []

    def test_tree_counts_skip_inactive_products(self, api_client, catalog):
        Product.objects.filter(sku="C-1").update(is_active=False)

        response = api_client.get(reverse("catalog-tree"))

        assert response.data[0]["product_count"] == 5


@pytest.mark.django_db
class TestAttributeListAPI:
    def test_attributes_keep_order_and_condition(self, api_client, catalog):
        response = api_client.get(reverse("catalog-attribute-list"))

        assert response.status_code == status.HTTP_200_OK
        assert [item["key"] for item in response.data] == [
            "system",
            "thread",
            "pitch",
            "length",
            "cores",
            "material",
        ]
        assert response.data[2]["requires"] == {"key": "system", "value": METRIC}
        assert response.data[0]["requires"] is None


@pytest.mark.django_db
class TestCategoryRetrieveAPI:
    def test_leaf_category_returns_trail_table_and_first_sku(self, api_client, catalog):
        response = api_client.get(reverse("catalog-category-detail", args=[BOLTS]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["path"] == ["consumables", "fasteners", "bolts"]
        assert [item["name"] for item in response.data["trail"]] == [
            "Расходники",
            "Крепёж",
            "Болты",
        ]
        assert response.data["is_leaf"] is True
        assert response.data["product_count"] == 4
        assert response.data["table"] == {"group_by": "thread", "columns": ["length", "material"]}
        # Dyuymli rezba birinchi, u "low" — buyurtma asosida emas.
        assert response.data["first_sku"] == "B-4"

    def test_branch_category_returns_children(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-category-detail", args=["consumables/fasteners"])
        )

        assert response.data["is_leaf"] is False
        assert response.data["first_sku"] is None
        assert [(child["slug"], child["product_count"]) for child in response.data["children"]] == [
            ("bolts", 4),
            ("nuts", 1),
        ]

    def test_unknown_path_returns_404(self, api_client, catalog):
        response = api_client.get(reverse("catalog-category-detail", args=["consumables/missing"]))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductListAPI:
    def test_leaf_list_is_in_table_order(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-list"), {"category": BOLTS})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 4
        # #10-24 (dyuym) → M6 (10 мм, 20 мм) → M10.
        assert skus(response.data["results"]) == ["B-4", "B-3", "B-2", "B-1"]

    def test_item_has_frontend_product_shape(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-product-list"), {"category": BOLTS, "attr_thread": "M10"}
        )

        (item,) = response.data["results"]
        assert item == {
            "sku": "B-1",
            "name": "Болт M10 x 20 мм",
            "path": ["consumables", "fasteners", "bolts"],
            "price": 300,
            "pack": 25,
            "stock": "in-stock",
            "category": {"slug": "bolts", "name": "Болты", "icon": "screws"},
            "attrs": {
                "system": METRIC,
                "thread": "M10",
                "pitch": "1.5 мм",
                "length": "20 мм",
                "material": "Сталь",
            },
        }

    def test_values_of_one_attribute_are_or_attributes_are_and(self, api_client, catalog):
        url = reverse("catalog-product-list")

        either = api_client.get(url, {"category": BOLTS, "attr_thread": ["M6", "M10"]})
        both = api_client.get(
            url, {"category": BOLTS, "attr_thread": "M6", "attr_material": "Сталь"}
        )

        assert skus(either.data["results"]) == ["B-3", "B-2", "B-1"]
        assert skus(both.data["results"]) == ["B-2"]

    def test_search_ignores_case_and_covers_whole_catalog(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-list"), {"q": "КАБЕЛЬ 2.5"})

        assert skus(response.data["results"]) == ["C-1"]

    def test_unknown_attribute_parameter_is_ignored(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-product-list"), {"category": BOLTS, "attr_color": "Белый"}
        )

        assert response.data["count"] == 4

    def test_pagination(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-list"), {"page_size": 2, "page": 2})

        assert response.data["count"] == 6
        assert skus(response.data["results"]) == ["B-3", "B-4"]

    def test_unknown_category_returns_404(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-list"), {"category": "nope"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFacetsAPI:
    def test_facets_without_filters(self, api_client, catalog):
        response = api_client.get(reverse("catalog-facets"), {"category": BOLTS})

        body = response.data
        assert response.status_code == status.HTTP_200_OK
        assert body["total"] == 4
        assert facet(body, "system") == [(INCH, 1, False), (METRIC, 3, False)]
        assert facet(body, "thread") == [("#10-24", 1, False), ("M6", 2, False), ("M10", 1, False)]
        assert facet(body, "length") == [('1"', 1, False), ("10 мм", 1, False), ("20 мм", 2, False)]
        # Qadam faqat metrik tizim tanlanganda chiqadi.
        assert facet(body, "pitch") is None
        assert body["first_sku"] == "B-4"

    def test_each_facet_counts_with_the_other_filters(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-facets"), {"category": BOLTS, "attr_system": METRIC}
        )

        body = response.data
        assert body["total"] == 3
        assert facet(body, "system") == [(INCH, 1, False), (METRIC, 3, True)]
        assert facet(body, "thread") == [("M6", 2, False), ("M10", 1, False)]
        assert facet(body, "pitch") == [("1 мм", 2, False), ("1.5 мм", 1, False)]
        assert body["first_sku"] == "B-3"

    def test_chosen_value_without_products_stays_with_zero(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-facets"), {"category": BOLTS, "attr_thread": "M99"}
        )

        body = response.data
        assert body["total"] == 0
        assert facet(body, "thread")[-1] == ("M99", 0, True)
        assert body["first_sku"] is None

    def test_made_to_order_product_opens_when_it_is_the_only_one(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-facets"),
            {"category": BOLTS, "attr_thread": "M6", "attr_material": "Сталь"},
        )

        assert response.data["first_sku"] == "B-2"

    def test_children_are_counted_with_filters(self, api_client, catalog):
        response = api_client.get(
            reverse("catalog-facets"), {"category": "consumables/fasteners", "q": "m6"}
        )

        assert [(child["slug"], child["count"]) for child in response.data["children"]] == [
            ("bolts", 2),
            ("nuts", 1),
        ]

    def test_unknown_category_returns_404(self, api_client, catalog):
        response = api_client.get(reverse("catalog-facets"), {"category": "nope"})

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductRetrieveAPI:
    def test_product_page_has_specs_variants_and_table(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-detail", args=["B-3"]))

        body = response.data
        assert response.status_code == status.HTTP_200_OK
        assert [spec["key"] for spec in body["specs"]] == [
            "system",
            "thread",
            "pitch",
            "length",
            "material",
        ]
        assert [item["slug"] for item in body["trail"]] == ["consumables", "fasteners", "bolts"]
        assert body["table"] == {"group_by": "thread", "columns": ["length", "material"]}
        assert body["variant_count"] == 4
        # Bog'liq "pitch" alohida chip qatori bo'lmaydi.
        assert [group["key"] for group in body["variants"]] == [
            "system",
            "thread",
            "length",
            "material",
        ]

        thread = next(group for group in body["variants"] if group["key"] == "thread")
        assert [
            (option["value"], option["sku"], option["selected"]) for option in thread["options"]
        ] == [
            ("#10-24", "B-4", False),
            ("M6", "B-3", True),
            ("M10", "B-1", False),
        ]
        material = next(group for group in body["variants"] if group["key"] == "material")
        # "Сталь" uchun eng ko'p tanlovni saqlaydigan variant: M6 rezbali B-2.
        assert ("Сталь", "B-2", False) in [
            (option["value"], option["sku"], option["selected"]) for option in material["options"]
        ]

    def test_inactive_product_returns_404(self, api_client, catalog):
        Product.objects.filter(sku="B-3").update(is_active=False)

        response = api_client.get(reverse("catalog-product-detail", args=["B-3"]))

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestRelatedAndFeaturedAPI:
    def test_related_skips_made_to_order_and_ranks_by_shared_values(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-related", args=["B-3"]))

        assert response.status_code == status.HTTP_200_OK
        assert skus(response.data) == ["B-1", "B-4"]

    def test_related_respects_limit(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-related", args=["B-3"]), {"limit": 1})

        assert skus(response.data) == ["B-1"]

    def test_related_for_unknown_product_returns_404(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-related", args=["NOPE"]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_featured_lists_marked_active_products(self, api_client, catalog):
        response = api_client.get(reverse("catalog-product-featured"))

        assert response.status_code == status.HTTP_200_OK
        assert skus(response.data) == ["B-4"]
        assert response.data[0]["attrs"]["thread"] == "#10-24"

    def test_featured_hides_inactive_products(self, api_client, catalog):
        Product.objects.filter(sku="B-4").update(is_active=False)

        response = api_client.get(reverse("catalog-product-featured"))

        assert response.data == []
