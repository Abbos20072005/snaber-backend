from django.db import transaction

from apps.product.models import Cart, CartItem, Favourite


@transaction.atomic
def merge_session_to_db(user, request):
    if not request.COOKIES.get("sessionid"):
        return
    session_favourite = Favourite.objects.filter(
        session_key=request.COOKIES.get("sessionid")
    )

    existing_id = set(
        Favourite.objects.filter(user=user).values_list("product_id", flat=True)
    )
    session_favourite.filter(product_id__in=existing_id).delete()
    session_favourite.update(user=user, session_key="")


@transaction.atomic
def merge_session_to_db_cart(user, request):
    if not request.COOKIES.get("sessionid"):
        return

    session_cart = Cart.objects.filter(
        session_key=request.COOKIES.get("sessionid")
    ).first()
    if not session_cart:
        return

    user_cart = Cart.objects.filter(user=user).first()

    if not user_cart:
        user_cart = Cart.objects.create(user=user)

    session_items = CartItem.objects.filter(cart=session_cart)

    for session_item in session_items:
        user_item = CartItem.objects.filter(
            cart=user_cart,
            product_id=session_item.product_id,
        ).first()

        if user_item:
            user_item.quantity += session_item.quantity
            user_item.save(update_fields=["quantity"])
            session_item.delete()
        else:
            session_item.cart = user_cart
            session_item.save(update_fields=["cart"])
    session_cart.delete()
