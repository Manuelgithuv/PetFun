from __future__ import annotations

import json
from decimal import Decimal

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from catalog.models import Product
from .models import CartItem
from .utils import get_or_create_cart


def _cart_payload(cart):
    items = []
    for it in cart.items.select_related('product').all():
        items.append({
            'product_id': it.product_id,
            'name': it.product.name,
            'quantity': it.quantity,
            'unit_price': f"{it.unit_price:.2f}",
            'subtotal': f"{it.subtotal:.2f}",
        })
    return {
        'total': f"{cart.total:.2f}",
        'items': items,
    }


@require_POST
def add(request):
    cart = get_or_create_cart(request)
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity') or 1)
    except Exception:
        return HttpResponseBadRequest('Invalid payload')

    product = Product.objects.filter(id=product_id).first()
    if not product:
        return HttpResponseBadRequest('Invalid product')
    if quantity < 1:
        quantity = 1
    # Prevent adding out-of-stock
    if product.stock <= 0:
        return HttpResponseBadRequest('Out of stock')

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity, 'unit_price': product.price, 'subtotal': Decimal('0')}
    )
    if not created:
        # Clamp total quantity to available stock
        new_q = item.quantity + quantity
        if new_q > product.stock:
            new_q = product.stock
        item.quantity = new_q
    item.unit_price = product.price
    item.save()
    cart.recalc_total()
    return JsonResponse(_cart_payload(cart))


@require_POST
def update(request):
    cart = get_or_create_cart(request)
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_id = int(data.get('product_id'))
        quantity = int(data.get('quantity'))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')

    if quantity < 1:
        quantity = 1

    item = cart.items.filter(product_id=product_id).select_related('product').first()
    if not item:
        return HttpResponseBadRequest('Item not in cart')

    # Clamp quantity to available stock
    max_q = item.product.stock
    if quantity > max_q:
        quantity = max_q
    item.quantity = quantity
    item.unit_price = item.product.price
    item.save()
    cart.recalc_total()
    return JsonResponse(_cart_payload(cart))


@require_POST
def remove(request):
    cart = get_or_create_cart(request)
    try:
        data = json.loads(request.body.decode('utf-8'))
        product_id = int(data.get('product_id'))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')
    cart.items.filter(product_id=product_id).delete()
    cart.recalc_total()
    return JsonResponse(_cart_payload(cart))
from django.shortcuts import render

# Create your views here.
