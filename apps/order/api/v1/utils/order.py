from apps.order.models import Order
from apps.product.models import Product, Variant


def detect_order_type(items_data):
    """Detect the order type based on the product types of the given order items."""
    variant_ids = [
        getattr(item.get("product_variant"), "pk", item.get("product_variant"))
        for item in items_data
        if item.get("product_variant")
    ]
    if not variant_ids:
        return Order.OrderType.READY
    product_types = set(
        Variant.objects.filter(id__in=variant_ids)
        .values_list("product__product_type", flat=True)
        .distinct()
    )
    if not product_types:
        return Order.OrderType.READY
    if product_types == {Product.ProductType.READY}:
        return Order.OrderType.READY
    if product_types == {Product.ProductType.MADE_TO_ORDER}:
        return Order.OrderType.RFQ
    if product_types == {Product.ProductType.BOTH}:
        return Order.OrderType.READY
    return Order.OrderType.BOTH
