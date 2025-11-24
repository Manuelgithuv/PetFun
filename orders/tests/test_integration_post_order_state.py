from __future__ import annotations

from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from cart.utils import get_or_create_cart
from orders.models import Order


@override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
class PostOrderStateIntegrationTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Pack Snacks",
            short_description="",
            description="",
            price=Decimal("8.00"),
            stock=2,
            category=self.cat,
            image_url="https://example.com/snacks.jpg",
            image="products/CAT-CAN-002_fNtjUeZ.jpg",
            sku="PO-STATE-1",
        )

    def _cart_with_qty(self, qty: int):
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=qty, unit_price=self.p.price, subtotal=self.p.price * qty)
        cart.recalc_total()
        self.client.session.save()
        return cart

    def test_confirm_clears_cart_and_sets_product_sold_out(self):
        cart = self._cart_with_qty(2)
        s = self.client.session
        s["checkout_email"] = "buyer@example.com"
        s["checkout_ship"] = {"name": "Buyer"}
        s.save()

        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total, cart.total)

        _ = self.client.get("/")
        req2 = self.client.request().wsgi_request
        cart2 = get_or_create_cart(req2)
        self.assertFalse(cart2.items.exists())
        self.assertEqual(cart2.total, Decimal("0"))

        self.p.refresh_from_db()
        self.assertEqual(self.p.stock, 0)
        self.assertEqual(self.p.status, Product.Status.SOLD_OUT)
