from apps.product.models import Cart, CartItem, Product


class CartRepository:
    def get_product(self, product_id):
        return Product.objects.filter(id=product_id, is_active=True).first()

    def get_cart_by_product(self, product_id, user=None, session_key=None):
        filters = {
            "product_id": product_id,
        }
        if user:
            filters["cart__user"] = user
        elif session_key:
            filters["cart__session_key"] = session_key
        else:
            return None
        return CartItem.objects.filter(**filters).first()

    def create_cart(self, user=None, session_key=None):
        data = {}
        if user:
            data["user"] = user
        if session_key:
            data["session_key"] = session_key
        return Cart.objects.create(**data)

    def create_cart_item(self, cart, product, quantity):
        return CartItem.objects.create(cart=cart, product=product, quantity=quantity)

    def get_cart(self, user=None, session_key=None):
        filters = {}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return Cart.objects.none()

        return Cart.objects.filter(**filters).first()

    def update_cart_quantity(self, cart_item, quantity):
        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])
        return cart_item

    def get_cart_items(self, user=None, session_key=None):
        filters = {}
        if user:
            filters["cart__user"] = user
        elif session_key:
            filters["cart__session_key"] = session_key
        else:
            return []

        return list(
            CartItem.objects.filter(**filters)
            .select_related("product__unit")
            .prefetch_related(
                "product__images",
                "product__characteristics",
                "product__product_attribute_values__attribute",
                "product__product_attribute_values__attribute_value",
            )
            .order_by("id")
        )

    def clear_cart(self, user=None, session_key=None):
        filters = {}
        if user:
            filters["cart__user"] = user
        elif session_key:
            filters["cart__session_key"] = session_key
        else:
            return

        CartItem.objects.filter(**filters).delete()
