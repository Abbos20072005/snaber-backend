import pytest
from django.urls import reverse
from rest_framework import status

from apps.catalog.models import Product
from apps.orders.api.v1.throttling import OrderRateThrottle
from apps.orders.models import Order, OrderStatus


def payload(**overrides):
    data = {
        "name": "  Алишер   Каримов ",
        "phone": "90 123-45-67",
        "comment": "Позвоните после обеда",
        "items": [{"sku": "B-1", "qty": 2}, {"sku": "B-3", "qty": 1}],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
class TestOrderCreateAPI:
    def test_create_order_success(self, api_client, catalog):
        response = api_client.post(reverse("order-create"), payload(), format="json")

        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get()
        assert response.data["number"] == order.pk
        assert response.data["status"] == OrderStatus.NEW
        assert response.data["total"] == 300 * 2 + 200
        assert [(item["sku"], item["price"], item["pack"], item["qty"], item["amount"]) for item in response.data["items"]] == [
            ("B-1", 300, 25, 2, 600),
            ("B-3", 200, 50, 1, 200),
        ]
        assert (order.name, order.phone, order.ip_address) == ("Алишер Каримов", "+998901234567", "127.0.0.1")

    def test_price_comes_from_database_not_from_client(self, api_client, catalog):
        items = [{"sku": "B-1", "qty": 1, "price": 1}]

        response = api_client.post(reverse("order-create"), payload(items=items), format="json")

        assert response.data["total"] == 300

    def test_same_product_in_two_lines_is_merged(self, api_client, catalog):
        items = [{"sku": "B-1", "qty": 2}, {"sku": "B-1", "qty": 3}]

        response = api_client.post(reverse("order-create"), payload(items=items), format="json")

        assert [(item["sku"], item["qty"]) for item in response.data["items"]] == [("B-1", 5)]

    def test_items_keep_values_from_order_time(self, api_client, catalog):
        api_client.post(reverse("order-create"), payload(), format="json")

        Product.objects.filter(sku="B-1").update(price=999, name="Новое имя")

        item = Order.objects.get().items.get(sku="B-1")
        assert (item.price, item.name) == (300, "Болт M10 x 20 мм")

    def test_unknown_or_inactive_sku_returns_400_for_that_line(self, api_client, catalog):
        Product.objects.filter(sku="B-3").update(is_active=False)
        items = [{"sku": "B-1", "qty": 1}, {"sku": "B-3", "qty": 1}, {"sku": "NOPE", "qty": 1}]

        response = api_client.post(reverse("order-create"), payload(items=items), format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        errors = response.data["items"]
        assert errors[0] == {}
        assert "sku" in errors[1] and "sku" in errors[2]
        assert not Order.objects.exists()

    def test_empty_cart_returns_400(self, api_client, catalog):
        response = api_client.post(reverse("order-create"), payload(items=[]), format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "items" in response.data

    @pytest.mark.parametrize("phone", ["12345", "+7 912 345 67 89", ""])
    def test_invalid_phone_returns_400(self, api_client, catalog, phone):
        response = api_client.post(reverse("order-create"), payload(phone=phone), format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone" in response.data

    def test_zero_quantity_returns_400(self, api_client, catalog):
        response = api_client.post(
            reverse("order-create"), payload(items=[{"sku": "B-1", "qty": 0}]), format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "qty" in response.data["items"][0]


@pytest.mark.django_db
class TestOrderThrottle:
    @pytest.fixture(autouse=True)
    def low_rate(self, monkeypatch):
        monkeypatch.setattr(OrderRateThrottle, "THROTTLE_RATES", {"orders": "2/hour"})

    def test_too_many_orders_return_429(self, api_client, catalog):
        url = reverse("order-create")
        for _ in range(2):
            assert api_client.post(url, payload(), format="json").status_code == status.HTTP_201_CREATED

        response = api_client.post(url, payload(), format="json")

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert Order.objects.count() == 2

    def test_rejected_forms_do_not_use_up_the_limit(self, api_client, catalog):
        url = reverse("order-create")
        for _ in range(3):
            api_client.post(url, payload(phone="1"), format="json")

        response = api_client.post(url, payload(), format="json")

        assert response.status_code == status.HTTP_201_CREATED
