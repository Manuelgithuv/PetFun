from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from cart.utils import get_or_create_cart


class CheckoutStartIntegrationTest(TestCase):
    def setUp(self):
        self.parent = Category.objects.create(name="Perros")
        self.sub = Category.objects.create(name="Juguetes", parent=self.parent)
        self.product = Product.objects.create(
            name="Pelota Start",
            short_description="",
            description="",
            price=Decimal("7.50"),
            stock=5,
            category=self.sub,
            image_url="http://example.com/p_start.png",
            sku="INT-START-001",
        )

    def test_checkout_start_renders_when_cart_has_items(self):
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        cart = get_or_create_cart(req)
        cart.items.create(product=self.product, quantity=1, unit_price=self.product.price, subtotal=self.product.price)
        cart.recalc_total()
        self.client.session.save()

        resp = self.client.get(reverse("orders:checkout_start"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("cart", resp.context)
        self.assertEqual(resp.context["cart"].total, cart.total)
