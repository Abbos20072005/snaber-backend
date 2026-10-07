from apps.product.models import Cart, CartItem, Variant


class CartRepository:
    def cart_product_exists(self, product, cart):
        filters = {"product": product}

        if cart:
            filters["cart"] = cart.id
        else:
            return False

        return CartItem.objects.filter(**filters).exists()

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

    def get_cart_list(self, user=None, session_key=None):
        filters = {}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return Cart.objects.none()

        return Cart.objects.filter(**filters).prefetch_related(
            "cartitem_set__product",
            "cartitem_set__company",
            "cartitem_set__attribute_stock__attribute_values__attribute",
        )

    def create_cart(self, user=None, session_key=None):
        data = {}
        if user:
            data["user"] = user
        if session_key:
            data["session_key"] = session_key
        return Cart.objects.create(**data)

    def create_cart_item(
        self,
        cart,
        product,
        quantity,
        company=None,
        user=None,
        session_key=None,
        attribute_stock=None,
        attributes=None,
        deadline=None,
    ):
        data = {
            "cart": cart,
            "product": product,
            "quantity": quantity,
            "company": company,
        }

        if attribute_stock:
            data["attribute_stock"] = attribute_stock
        if attributes:
            data["attributes"] = attributes
        if deadline:
            data["deadline"] = deadline
        if user:
            data["user"] = user
        elif session_key:
            data["session_key"] = session_key

        return CartItem.objects.create(**data)

    def get_cart(self, user=None, session_key=None):
        filters = {}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return Cart.objects.none()

        return Cart.objects.filter(**filters).first()

    def update_cart_quantity(self, cart, quantity):
        cart.quantity = quantity
        cart.save(update_fields=["quantity"])
        return cart

    def get_product_variant(self, product):
        return Variant.objects.filter(product=product).first()

    def get_product_variant_by_product_id(self, product_id):
        return Variant.objects.filter(product_id=product_id).first()

    def get_cart_items_grouped_by_company(self, user=None, session_key=None):
        filters = {}
        if user:
            filters["cart__user"] = user
        elif session_key:
            filters["cart__session_key"] = session_key
        else:
            return {}

        items = (
            CartItem.objects.filter(**filters)
            .select_related("product", "company", "product__product__owner")
            .prefetch_related("attribute_stock__attribute_values__attribute")
            .all()
        )

        grouped = {}
        for item in items:
            company = item.company or item.product.product.owner
            if company not in grouped:
                grouped[company] = []
            grouped[company].append(item)

        return grouped

    def clear_cart(self, user=None, session_key=None):
        filters = {}
        if user:
            filters["cart__user"] = user
        elif session_key:
            filters["cart__session_key"] = session_key
        else:
            return

        CartItem.objects.filter(**filters).delete()
