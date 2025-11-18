from __future__ import annotations

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from orders.models import Order, OrderItem


class TrackOrderIntegrationTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Perros")
        self.prod = Product.objects.create(
            name="Arnés",
            short_description="",
            description="",
            price=Decimal("19.99"),
            stock=10,
            category=self.cat,
            image_url="https://example.com/arnes.jpg",
            sku="TI-ARN-1",
        )

    def test_track_order_found_shows_order_details(self):
        order = Order.objects.create(
            user=None,
            contact_email="buyer@example.com",
            total=Decimal("19.99"),
            status=Order.Status.RECEIVED,
            ship_name="Buyer",
            ship_street="Calle 1",
            ship_number="1",
            ship_floor="",
            ship_city="Madrid",
            ship_postal_code="28001",
            ship_country="ES",
            payment_method=Order.PaymentMethod.CARD,
        )
        OrderItem.objects.create(
            order=order,
            product=self.prod,
            product_name=self.prod.name,
            quantity=1,
            unit_price=self.prod.price,
            subtotal=self.prod.price,
        )
        res_get = self.client.get(reverse("orders:track_order"))
        self.assertEqual(res_get.status_code, 200)
        res_post = self.client.post(reverse("orders:track_order"), data={"code": order.tracking_code}, follow=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertContains(res_post, order.tracking_code)
        self.assertContains(res_post, self.prod.name)
