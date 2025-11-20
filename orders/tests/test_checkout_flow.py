from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from cart.utils import get_or_create_cart
from orders.models import Order


@override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
class CheckoutFlowTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.parent = Category.objects.create(name="Perros")
		self.sub = Category.objects.create(name="Accesorios", parent=self.parent)
		self.p1 = Product.objects.create(
			name="Collar",
			short_description="",
			description="",
			price=Decimal("15.00"),
			stock=5,
			category=self.sub,
			image_url="https://example.com/collar.jpg",
			sku="",
		)

	def _create_cart_with_item(self):
		_ = self.client.get("/")
		req = self.client.request().wsgi_request
		cart = get_or_create_cart(req)
		cart.items.create(product=self.p1, quantity=2, unit_price=self.p1.price, subtotal=Decimal("30.00"))
		cart.recalc_total()
		self.client.session.save()
		return cart

	@patch("orders.views.stripe.PaymentIntent.create")
	def test_payment_step_creates_intent_and_renders_elements(self, mock_create):
		cart = self._create_cart_with_item()
		mock_create.return_value = type("PI", (), {"id": "pi_123", "client_secret": "cs_123"})
		url = reverse("orders:checkout_payment")
		payload = {
			"email": "test@example.com",
			"ship_name": "Test User",
			"ship_street": "Calle 1",
			"ship_number": "10",
			"ship_floor": "",
			"ship_city": "Madrid",
			"ship_postal_code": "28001",
			"ship_country": "ES",
		}
		res = self.client.post(url, data=payload)
		self.assertEqual(res.status_code, 200)
		self.assertIn("stripe_client_secret", res.context)
		self.assertEqual(res.context["stripe_client_secret"], "cs_123")
		mock_create.assert_called_once()

	@patch("orders.views.stripe.PaymentIntent.capture")
	@patch("orders.views.stripe.PaymentIntent.retrieve")
	@patch("orders.views.stripe.PaymentIntent.create")
	def test_confirm_captures_and_creates_order(self, mock_create, mock_retrieve, mock_capture):
		cart = self._create_cart_with_item()
		mock_create.return_value = type("PI", (), {"id": "pi_456", "client_secret": "cs_456"})
		pay_url = reverse("orders:checkout_payment")
		payload = {
			"email": "buyer@example.com",
			"ship_name": "Buyer",
			"ship_street": "Calle 1",
			"ship_number": "10",
			"ship_floor": "",
			"ship_city": "Madrid",
			"ship_postal_code": "28001",
			"ship_country": "ES",
		}
		res = self.client.post(pay_url, data=payload)
		self.assertEqual(res.status_code, 200)
		session = self.client.session
		pi_id = session.get("payment_intent_id")
		self.assertIsNotNone(pi_id)

		mock_retrieve.return_value = {
			"id": pi_id,
			"status": "requires_capture",
			"amount": int(cart.total * 100),
		}
		confirm_url = reverse("orders:checkout_confirm")
		res2 = self.client.get(confirm_url)
		self.assertEqual(res2.status_code, 200)
		self.assertEqual(Order.objects.count(), 1)
		order = Order.objects.first()
		self.assertEqual(order.total, cart.total)
		self.p1.refresh_from_db()
		self.assertEqual(self.p1.stock, 3)
		mock_capture.assert_called()
