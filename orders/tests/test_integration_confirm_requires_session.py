from __future__ import annotations

from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from cart.utils import get_or_create_cart


@override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
class ConfirmRequiresSessionIntegrationTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Correa",
            short_description="",
            description="",
            price=Decimal("11.00"),
            stock=3,
            category=self.cat,
            image_url="https://example.com/correa.jpg",
            sku="CONF-SESS-1",
        )

    def _cart_with_item(self):
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=1, unit_price=self.p.price, subtotal=self.p.price)
        cart.recalc_total()
        self.client.session.save()
        return cart

    def test_confirm_without_email_or_ship_redirects_to_payment(self):
        self._cart_with_item()
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res["Location"], reverse("orders:checkout_payment"))
