import json
from types import SimpleNamespace
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.models import Category, Product
from orders.models import Order


@override_settings(STRIPE_SECRET_KEY="sk_test_dummy", STRIPE_PUBLISHABLE_KEY="pk_test_dummy")
class CartApiToCheckoutIntegrationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="e2e@example.com",
            password="demo12345",
            first_name="E2E",
            last_name="Tester",
            phone="000",
            address="Calle",
            city="Ciudad",
            postal_code="00000",
        )
        cat = Category.objects.create(name="Perros")
        self.product = Product.objects.create(
            sku="INT-E2E-001",
            name="Juguete E2E",
            short_description="",
            description="",
            price=Decimal("12.00"),
            stock=10,
            category=cat,
            image_url="http://example.com/e2e.png",
        )

    def test_add_via_api_then_full_checkout_with_stripe_mock(self):
        add_url = reverse("cart:add")
        payload = {"product_id": self.product.id, "quantity": 2}
        resp = self.client.post(add_url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("total", data)
        self.assertEqual(len(data["items"]), 1)
        with patch("orders.views.stripe") as mock_stripe:
            mock_stripe.PaymentIntent.create.return_value = SimpleNamespace(id="pi_e2e_1", client_secret="cs_e2e_1")
            payment_post = self.client.post(
                reverse("orders:checkout_payment"),
                data={
                    "email": "buyer@e2e.com",
                    "ship_name": "Buyer E2E",
                    "ship_street": "Calle X",
                    "ship_number": "1",
                    "ship_floor": "",
                    "ship_city": "Ciudad",
                    "ship_postal_code": "00000",
                    "ship_country": "ES",
                },
            )
            self.assertEqual(payment_post.status_code, 200)
            session = self.client.session
            self.assertEqual(session.get("payment_intent_id"), "pi_e2e_1")

            expected_amount = int(Decimal("12.00") * 100) * 2
            mock_stripe.PaymentIntent.retrieve.return_value = {"id": "pi_e2e_1", "amount": expected_amount, "status": "requires_capture"}

            confirm_resp = self.client.get(reverse("orders:checkout_confirm"))
            self.assertEqual(confirm_resp.status_code, 200)

            mock_stripe.PaymentIntent.capture.assert_called_with("pi_e2e_1")

        orders = Order.objects.filter(contact_email="buyer@e2e.com")
        self.assertEqual(orders.count(), 1)
        order = orders.first()
        self.assertEqual(order.total, Decimal("24.00"))
