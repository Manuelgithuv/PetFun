from __future__ import annotations

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.models import Category, Product
from orders.models import Order, OrderItem


class AccountDeleteOrdersIntegrationTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.password = "StrongPass9"
        self.user = self.User.objects.create_user(
            email="buyer@petfun.test",
            password=self.password,
            first_name="Buyer",
            last_name="Test",
            phone="600000000",
            address="Calle 1",
            city="Madrid",
            postal_code="28001",
        )
        cat = Category.objects.create(name="Perros")
        prod = Product.objects.create(
            name="Arnés Deluxe",
            short_description="",
            description="",
            price=Decimal("29.90"),
            stock=5,
            category=cat,
            image_url="https://example.com/a-deluxe.jpg",
            image="products/CAT-CAN-002_fNtjUeZ.jpg",
            sku="AC-DEL-1",
        )
        self.order = Order.objects.create(
            user=self.user,
            contact_email=self.user.email,
            total=prod.price,
            status=Order.Status.RECEIVED,
            ship_name="Buyer Test",
            ship_street="Calle 1",
            ship_number="1",
            ship_floor="",
            ship_city="Madrid",
            ship_postal_code="28001",
            ship_country="ES",
            payment_method=Order.PaymentMethod.CARD,
        )
        OrderItem.objects.create(
            order=self.order,
            product=prod,
            product_name=prod.name,
            quantity=1,
            unit_price=prod.price,
            subtotal=prod.price,
        )

    def test_deleting_account_does_not_delete_orders(self):
        logged = self.client.login(email=self.user.email, password=self.password)
        self.assertTrue(logged)
        resp = self.client.post(reverse("account_delete"), data={"password": self.password}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.User.objects.filter(email=self.user.email).exists())
        self.assertTrue(Order.objects.filter(pk=self.order.pk).exists())
        o = Order.objects.get(pk=self.order.pk)
        self.assertIsNone(o.user)
