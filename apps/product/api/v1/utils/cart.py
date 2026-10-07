def get_cart_item_total_price(item):
    product = item.product
    if not product:
        return None
    price = (
        getattr(product, "price_override", None)
        or getattr(product.product, "price_min", None)
        or 0
    )
    return item.quantity * price
