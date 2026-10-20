def get_cart_item_total_price(item):
    return item.quantity * item.product.final_price
