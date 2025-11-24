from __future__ import annotations

from decimal import Decimal

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from catalog.models import Category, Product


class OrdersMoreBranchesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Pelota",
            short_description="",
            description="",
            price=Decimal("3.00"),
            stock=5,
            category=self.cat,
            image_url="https://example.com/pelota2.jpg",
            image="products/CAT-CAN-002_fNtjUeZ.jpg",
            sku="SKU-X",
        )

    def test_checkout_start_redirects_when_cart_empty(self):
        res = self.client.get(reverse("orders:checkout_start"))
        self.assertEqual(res.status_code, 302)

    def test_checkout_payment_prefills_for_authenticated_user(self):
        # create and login user
        from django.contrib.auth import get_user_model

        U = get_user_model()
        u = U.objects.create_user(email="x@y.com", password="p", first_name="X", last_name="Y", address="Calle A", city="Z", postal_code="000")
        self.client.login(email="x@y.com", password="p")
        # ensure cart has items
        from cart.utils import get_or_create_cart
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=1, unit_price=self.p.price, subtotal=self.p.price)
        cart.recalc_total()
        res = self.client.get(reverse("orders:checkout_payment"))
        self.assertEqual(res.status_code, 200)
        self.assertIn("initial", res.context)
        self.assertEqual(res.context["initial"].get("email"), "x@y.com")

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    def test_checkout_confirm_adjusts_cart_and_redirects_on_stock_change(self):
        # add 2 units then reduce stock to 1 to force adjustment
        from cart.utils import get_or_create_cart

        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=2, unit_price=self.p.price, subtotal=self.p.price * 2)
        cart.recalc_total()
        # prepare session data
        s = self.client.session
        s["checkout_email"] = "a@b.com"
        s["checkout_ship"] = {"name": "A"}
        s.save()
        # reduce stock
        self.p.stock = 1
        self.p.save()
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)
        # back to start to review adjustments
