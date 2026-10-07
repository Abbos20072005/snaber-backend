from apps.product.models import Favourite, Product


class FavouriteRepository:
    def get_product(self, product_id):
        return Product.objects.filter(id=product_id).first()

    def favourite_exists(self, product_id, user=None, session_key=None):
        filters = {"product_id": product_id}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return False

        return Favourite.objects.filter(**filters).exists()

    def create_favourite(self, product, user=None, session_key=None):
        return Favourite.objects.create(
            product=product, user=user, session_key=session_key
        )

    def get_favourite_list(self, user=None, session_key=None):
        filters = {}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return Favourite.objects.none()

        return Favourite.objects.filter(**filters).select_related("product")

    def get_favourite_by_product(self, product_id, user=None, session_key=None):
        filters = {"product_id": product_id}

        if user:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return None

        return Favourite.objects.filter(**filters).first()

    def delete_favourite(self, product_id: int, user=None, session_key=None):
        filters = {"product_id": product_id}

        if user and user.is_authenticated:
            filters["user"] = user
        elif session_key:
            filters["session_key"] = session_key
        else:
            return False

        Favourite.objects.filter(**filters).delete()

        return True
