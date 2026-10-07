from django.db import transaction

from apps.company.models import CompanyMember
from apps.order.api.v1.filters.order import OrderFilter
from apps.order.models import Order, OrderItem, RFQOrderItemAttribute


class OrderRepository:
    def _create_item_attributes(self, order_item, attributes_data):
        if not attributes_data:
            return
        objs = []
        for attr_data in attributes_data:
            attr = attr_data["attribute"]
            value_opt = attr_data.get("value_option")
            kwargs = {
                "order_item": order_item,
                "value": attr_data.get("value", ""),
            }
            if isinstance(attr, int):
                kwargs["attribute_id"] = attr
            else:
                kwargs["attribute"] = attr
            if isinstance(value_opt, int):
                kwargs["value_option_id"] = value_opt
            elif value_opt is not None:
                kwargs["value_option"] = value_opt
            objs.append(RFQOrderItemAttribute(**kwargs))
        RFQOrderItemAttribute.objects.bulk_create(objs)

    def _update_item_attributes(self, order_item, attributes_data):
        with transaction.atomic():
            order_item.attributes.all().delete()
            self._create_item_attributes(order_item, attributes_data)

    def get_all(self, user, query_params):
        qs = (
            Order.objects.select_related("buyer", "company")
            .prefetch_related(
                "items__product_variant__product",
                "items__product_variant__product_variant_medias",
                "items__category",
                "items__attributes__attribute",
                "items__attributes__value_option",
            )
            .order_by("-created_at")
        )

        if CompanyMember.objects.filter(user=user).exists():
            user_company_ids = user.company_memberships.values_list(
                "company_id", flat=True
            )
            qs = qs.filter(company_id__in=user_company_ids)
        else:
            qs = qs.filter(buyer=user)

        return OrderFilter(query_params, queryset=qs).qs

    def get_by_id(self, pk):
        return (
            Order.objects.select_related("buyer", "company")
            .prefetch_related(
                "items__product_variant__product",
                "items__product_variant__product_variant_medias",
                "items__category",
                "items__attributes__attribute",
                "items__attributes__value_option",
            )
            .filter(id=pk)
            .first()
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr != "items":
                setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, buyer, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(buyer=buyer, **validated_data)
        self._handle_items(order, items_data)
        return order

    def _handle_items(self, order, items_data):
        for item_data in items_data:
            item_attrs = item_data.pop("attributes", [])
            order_item = OrderItem.objects.create(order=order, **item_data)
            self._create_item_attributes(order_item, item_attrs)

    def update_item_attributes(self, order_item_id, attributes_data):
        order_item = OrderItem.objects.filter(id=order_item_id).first()
        if order_item:
            self._update_item_attributes(order_item, attributes_data)

    def create_order_from_cart_group(
        self, buyer, company, items_data, order_type="ready"
    ):
        with transaction.atomic():
            order = Order.objects.create(
                buyer=buyer,
                company=company,
                order_type=order_type,
            )
            for item_data in items_data:
                item_attrs = item_data.pop("attributes", [])
                order_item = OrderItem.objects.create(order=order, **item_data)
                self._create_item_attributes(order_item, item_attrs)
            return order

    def delete(self, pk):
        order = self.get_by_id(pk)
        if order:
            order.delete()
            return True
        return False

    def get_order_item(self, order_id, item_id):
        return (
            OrderItem.objects.filter(id=item_id, order_id=order_id)
            .select_related("product_variant__product")
            .first()
        )

    def update_item_quantity(self, item, quantity):
        item.quantity = quantity
        item.save()
        return item

    def add_item(self, order, item_data):
        item_attrs = item_data.pop("attributes", [])
        order_item = OrderItem.objects.create(order=order, **item_data)
        self._create_item_attributes(order_item, item_attrs)
        return order_item

    def delete_item(self, item):
        item.delete()

    def get_all_by_ids(self, ids):
        return (
            Order.objects.filter(id__in=ids)
            .select_related("buyer", "company")
            .prefetch_related(
                "items__product_variant__product",
                "items__product_variant__product_variant_medias",
                "items__category",
                "items__attributes__attribute",
                "items__attributes__value_option",
            )
        )
