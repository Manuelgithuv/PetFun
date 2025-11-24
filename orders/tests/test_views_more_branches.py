from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from cart.utils import get_or_create_cart
from orders.models import Order


class OrdersViewsMoreBranchesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Cama",
            short_description="",
            description="",
            price=Decimal("25.00"),
            stock=5,
            category=self.cat,
            image_url="https://example.com/cama.jpg",
            image="products/CAT-CAN-002_fNtjUeZ.jpg",
            sku="",
        )

    def _cart_with_qty(self, qty: int):
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=qty, unit_price=self.p.price, subtotal=self.p.price * qty)
        cart.recalc_total()
        self.client.session.save()
        return cart

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
    @patch("orders.views.stripe.PaymentIntent.retrieve")
    def test_confirm_retrieve_exception_redirects(self, mock_retrieve):
        self._cart_with_qty(1)
        s = self.client.session
        s["checkout_email"] = "a@b.com"
        s["checkout_ship"] = {"name": "A"}
        s["payment_intent_id"] = "pi_fail"
        s.save()
        mock_retrieve.side_effect = Exception("boom")
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
    @patch("orders.views.stripe.PaymentIntent.capture")
    @patch("orders.views.stripe.PaymentIntent.retrieve")
    def test_confirm_capture_exception_redirects(self, mock_retrieve, mock_capture):
        cart = self._cart_with_qty(1)
        s = self.client.session
        s["checkout_email"] = "a@b.com"
        s["checkout_ship"] = {"name": "A"}
        s["payment_intent_id"] = "pi_x"
        s.save()
        mock_retrieve.return_value = {"id": "pi_x", "status": "requires_capture", "amount": int(cart.total * 100)}
        mock_capture.side_effect = Exception("fail cap")
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    def test_confirm_adjusts_but_not_empty_redirects(self):
        # put 3 in cart, reduce stock to 1, expect adjustment and redirect back to start
        self._cart_with_qty(3)
        s = self.client.session
        s["checkout_email"] = "buyer@example.com"
        s["checkout_ship"] = {"name": "Buyer"}
        s.save()
        # Reduce stock to 1
        self.p.stock = 1
        self.p.save()
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)
        # redirected to start due to adjustment message

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    @patch("orders.views.send_mail")
    def test_confirm_without_stripe_creates_order_and_sends_mail(self, mock_send_mail):
        cart = self._cart_with_qty(2)
        s = self.client.session
        s["checkout_email"] = "ok@example.com"
        s["checkout_ship"] = {"name": "OK"}
        s.save()
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        mock_send_mail.assert_called()

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    @patch("orders.views.send_mail")
    def test_confirm_mail_failure_is_ignored(self, mock_send_mail):
        cart = self._cart_with_qty(1)
        s = self.client.session
        s["checkout_email"] = "ok@example.com"
        s["checkout_ship"] = {"name": "OK"}
        s.save()
        mock_send_mail.side_effect = Exception("smtp down")
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

    def test_track_order_not_found_shows_page(self):
        res = self.client.get(reverse("orders:track_order"))
        self.assertEqual(res.status_code, 200)
        res2 = self.client.post(reverse("orders:track_order"), data={"code": "NOPE"}, follow=True)
        self.assertEqual(res2.status_code, 200)
