from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from orders.models import Order, OrderItem
from orders.apps import _seed_orders_if_empty
from django.test import override_settings


class OrdersModelsTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Juguete",
            short_description="",
            description="",
            price=Decimal("5.00"),
            stock=10,
            category=self.cat,
            image_url="https://example.com/juguete.jpg",
            sku="SKU-1",
        )

    def test_order_and_item_str_and_save(self):
        o = Order.objects.create(
            user=None,
            contact_email="a@b.com",
            total=Decimal("0.00"),
            status=Order.Status.RECEIVED,
            ship_name="A",
            ship_street="B",
            ship_number="1",
            ship_floor="",
            ship_city="C",
            ship_postal_code="00000",
            ship_country="ES",
            payment_method=Order.PaymentMethod.CARD,
        )
        self.assertTrue(o.tracking_code)
        s = str(o)
        self.assertIn("Pedido", s)

        item = OrderItem.objects.create(order=o, product=self.p, product_name="", quantity=2, unit_price=Decimal("0"), subtotal=Decimal("0"))
        self.assertEqual(item.product_name, self.p.name)
        self.assertEqual(item.unit_price, self.p.price)
        self.assertEqual(item.subtotal, self.p.price * 2)


class OrdersAppsSeedTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Perros")
        Product.objects.create(
            name="Juguete",
            short_description="",
            description="",
            price=Decimal("5.00"),
            stock=10,
            category=self.cat,
            image_url="https://example.com/juguete.jpg",
            sku="SKU-2",
        )

    def test_seed_orders_if_empty_creates_demo_orders(self):
        self.assertFalse(Order.objects.exists())
        with override_settings(DEBUG=True):
            _seed_orders_if_empty(sender=None)
        self.assertTrue(Order.objects.exists())


class OrdersViewsErrorBranchesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Perros")
        self.p = Product.objects.create(
            name="Juguete",
            short_description="",
            description="",
            price=Decimal("5.00"),
            stock=10,
            category=self.cat,
            image_url="https://example.com/juguete2.jpg",
            sku="SKU-3",
        )

    def _add_cart(self, qty=1):
        from cart.utils import get_or_create_cart
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.p, quantity=qty, unit_price=self.p.price, subtotal=self.p.price * qty)
        cart.recalc_total()
        self.client.session.save()
        return cart

    @override_settings(STRIPE_SECRET_KEY="", STRIPE_PUBLISHABLE_KEY="")
    def test_checkout_payment_without_stripe_keys_renders_warning(self):
        self._add_cart(1)
        url = reverse("orders:checkout_payment")
        res = self.client.post(url, data={
            "email": "x@y.com",
            "ship_name": "A",
            "ship_street": "B",
            "ship_number": "1",
            "ship_city": "C",
            "ship_postal_code": "000",
            "ship_country": "ES",
        })
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Stripe no está configurado")

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
    @patch("orders.views.stripe.PaymentIntent.retrieve")
    def test_checkout_confirm_missing_pi_in_session_redirects(self, mock_retrieve):
        self._add_cart(1)
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
    @patch("orders.views.stripe.PaymentIntent.retrieve")
    def test_checkout_confirm_amount_mismatch_redirects(self, mock_retrieve):
        cart = self._add_cart(1)
        # prepare session values
        session = self.client.session
        session["checkout_email"] = "a@b.com"
        session["checkout_ship"] = {"name": "A"}
        session["payment_intent_id"] = "pi_x"
        session.save()
        mock_retrieve.return_value = {"id": "pi_x", "status": "requires_capture", "amount": int(cart.total * 100) + 100}
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
    @patch("orders.views.stripe.PaymentIntent.retrieve")
    def test_checkout_confirm_status_not_ready_redirects(self, mock_retrieve):
        cart = self._add_cart(1)
        session = self.client.session
        session["checkout_email"] = "a@b.com"
        session["checkout_ship"] = {"name": "A"}
        session["payment_intent_id"] = "pi_y"
        session.save()
        mock_retrieve.return_value = {"id": "pi_y", "status": "processing", "amount": int(cart.total * 100)}
        res = self.client.get(reverse("orders:checkout_confirm"))
        self.assertEqual(res.status_code, 302)
