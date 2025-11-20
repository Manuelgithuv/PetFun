import os
from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.filter
def get_item(d, key):
    try:
        return d.get(key, [])
    except Exception:
        return []


@register.simple_tag
def product_image_src(product):
    """Return URL for product image from Images/ by SKU with fallbacks.

    Looks for files named by SKU with extensions .webp, .jpg, .jpeg, .png in
    BASE_DIR/Images. If found, serves via static URL. Otherwise falls back to
    product.image_url or a placeholder with the SKU text.
    """
    sku = getattr(product, "sku", None) or str(product)

    img_dir = os.path.join(settings.BASE_DIR, "Images")
    for ext in (".webp", ".jpg", ".jpeg", ".png"):
        candidate = os.path.join(img_dir, sku + ext)
        try:
            if os.path.exists(candidate):
                return static(sku + ext)
        except Exception:
            # If any filesystem issue occurs, ignore and continue fallbacks
            pass

    url = getattr(product, "image_url", "") or f"https://placehold.co/600x400?text={sku}"
    return url
