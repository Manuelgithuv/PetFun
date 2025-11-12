from __future__ import annotations

from .utils import get_or_create_cart


def cart(request):
    try:
        c = get_or_create_cart(request)
        return {
            'cart': c,
            'cart_item_count': c.items.count(),
        }
    except Exception:
        # In case of migrations pending
        return {'cart': None, 'cart_item_count': 0}
