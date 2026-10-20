import html

import pytest
from django.urls import reverse

from apps.catalog.models import Product
from apps.orders.models import OrderStatus
from apps.orders.services import create_order


@pytest.fixture
def order(catalog):
    return create_order(
        name="Алишер",
        phone="+998901234567",
        comment="",
        lines=[(Product.objects.get(sku="B-1"), 2)],
    )


def change_status(admin_client, order, new_status):
    return admin_client.post(
        reverse("admin:orders_order_change", args=[order.pk]),
        {
            "status": new_status,
            "items-TOTAL_FORMS": 1,
            "items-INITIAL_FORMS": 1,
            "items-0-id": order.items.get().pk,
            "items-0-order": order.pk,
        },
    )


@pytest.mark.django_db
class TestOrderAdmin:
    def test_changelist_shows_order(self, admin_client, order):
        response = admin_client.get(reverse("admin:orders_order_changelist"))

        content = html.unescape(response.content.decode())
        assert response.status_code == 200
        assert f"№{order.pk}" in content
        assert "600 so'm" in content

    def test_search_by_phone_part_with_spaces(self, admin_client, order):
        response = admin_client.get(reverse("admin:orders_order_changelist"), {"q": "90 123 45"})

        assert list(response.context["cl"].result_list) == [order]

    def test_orders_cannot_be_added_in_admin(self, admin_client, catalog):
        response = admin_client.get(reverse("admin:orders_order_add"))

        assert response.status_code == 403

    def test_new_order_can_be_confirmed(self, admin_client, admin_user, order):
        response = change_status(admin_client, order, OrderStatus.CONFIRMED)

        assert response.status_code == 302
        order.refresh_from_db()
        assert (order.status, order.modified_by) == (OrderStatus.CONFIRMED, admin_user)

    def test_new_order_cannot_jump_to_done(self, admin_client, order):
        response = change_status(admin_client, order, OrderStatus.DONE)

        assert response.status_code == 200
        order.refresh_from_db()
        assert order.status == OrderStatus.NEW

    def test_status_choices_follow_allowed_transitions(self, admin_client, order):
        response = admin_client.get(reverse("admin:orders_order_change", args=[order.pk]))

        choices = [value for value, _ in response.context["adminform"].form.fields["status"].choices]
        assert choices == [OrderStatus.NEW, OrderStatus.CONFIRMED, OrderStatus.CANCELLED]
