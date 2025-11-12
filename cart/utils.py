from __future__ import annotations

from django.utils.crypto import get_random_string

from .models import Cart


def get_or_create_cart(request) -> Cart:
    """Return a cart associated to the logged user or session.
    Creates the session key if missing.
    """
    if not request.session.session_key:
        # ensure session exists
        request.session.create()
    session_key = request.session.session_key

    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).order_by('-id').first()
        if not cart:
            cart = Cart.objects.create(user=request.user, session_key=session_key)
        else:
            # ensure session_key is set to help identify
            if not cart.session_key:
                cart.session_key = session_key
                cart.save(update_fields=["session_key"])
    else:
        cart, _ = Cart.objects.get_or_create(session_key=session_key, defaults={})

    return cart
