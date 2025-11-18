from __future__ import annotations

import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from catalog.models import Category, Product
from cart.models import Cart
from cart.utils import get_or_create_cart


class CartLoginBehaviorIntegrationTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.password = "demo12345"
        self.user = User.objects.create_user(
            email="anon2user@example.com",
            password=self.password,
            first_name="Anon",
            last_name="User",
            phone="000",
            address="Calle",
            city="Ciudad",
            postal_code="00000",
        )
        cat = Category.objects.create(name="Perros")
        self.product = Product.objects.create(
            name="Snack",
            short_description="",
            description="",
            price=Decimal("3.50"),
            stock=10,
            category=cat,
            image_url="http://example.com/snack.png",
            sku="AN-LOGIN-1",
        )

    def test_anonymous_cart_is_not_merged_on_login_new_user_cart_created(self):
        add_url = reverse("cart:add")
        payload = {"product_id": self.product.id, "quantity": 2}
        resp = self.client.post(add_url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        _ = self.client.get("/")
        req = self.client.request().wsgi_request
        anon_cart = get_or_create_cart(req)
        self.assertIsNone(anon_cart.user)
        self.assertTrue(anon_cart.items.exists())

        login_resp = self.client.post(reverse("login"), data={"email": self.user.email, "password": self.password})
        self.assertEqual(login_resp.status_code, 302)

        _ = self.client.get("/")
        req2 = self.client.request().wsgi_request
        user_cart = get_or_create_cart(req2)
        self.assertIsNotNone(user_cart.user)
        self.assertEqual(user_cart.user.email, self.user.email)
        self.assertFalse(user_cart.items.exists())

        self.assertTrue(Cart.objects.filter(pk=anon_cart.pk, user__isnull=True).exists())
        self.assertTrue(anon_cart.items.exists())
