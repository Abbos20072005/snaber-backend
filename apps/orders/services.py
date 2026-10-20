from django.db import transaction

from apps.orders.models import Order, OrderItem


@transaction.atomic
def create_order(*, name, phone, comment, lines, ip_address=None):
    """Create an order from `(product, qty)` pairs.

    Narx har doim bazadan olinadi: mijoz savatidagi narx eskirgan yoki
    o'zgartirilgan bo'lishi mumkin. Nomi, artikuli, narxi va qadog'i qatorga
    ko'chiriladi, keyin katalog o'zgarsa ham buyurtma o'zgarmaydi.
    """
    order = Order.objects.create(name=name, phone=phone, comment=comment, ip_address=ip_address)
    items = [
        OrderItem(
            order=order,
            product=product,
            sku=product.sku,
            name=product.name,
            price=product.price,
            pack=product.pack,
            qty=qty,
            amount=product.price * qty,
        )
        for product, qty in lines
    ]
    OrderItem.objects.bulk_create(items)
    order.total = sum(item.amount for item in items)
    order.save(update_fields=["total", "modified_at"])
    return order
