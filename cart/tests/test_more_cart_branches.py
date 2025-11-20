from __future__ import annotations

import json
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from catalog.models import Category, Product


class CartMoreBranchesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Category.objects.create(name="Perros")
        self.sub = Category.objects.create(name="Juguetes", parent=self.cat)
        self.p = Product.objects.create(
            name="Mordedor",
            short_description="",
            description="",
            price=Decimal("4.50"),
            stock=2,
            category=self.sub,
            image_url="https://example.com/mordedor2.jpg",
            sku="",
        )

    def _post(self, name: str, payload, as_json=True):
        url = reverse(f"cart:{name}")
        if as_json:
            return self.client.post(url, data=json.dumps(payload), content_type="application/json")
        else:
            # malformed body (not JSON)
            return self.client.post(url, data=payload, content_type="application/json")

    def test_update_item_not_in_cart_returns_400(self):
        res = self._post("update", {"product_id": self.p.id, "quantity": 1})
        self.assertEqual(res.status_code, 400)

    def test_add_malformed_payload_returns_400(self):
        res = self._post("add", "not-json", as_json=False)
        self.assertEqual(res.status_code, 400)

    def test_remove_malformed_payload_returns_400(self):
        res = self._post("remove", "not-json", as_json=False)
        self.assertEqual(res.status_code, 400)

    def test_add_quantity_below_one_clamps_to_one(self):
        res = self._post("add", {"product_id": self.p.id, "quantity": 0})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["items"][0]["quantity"], 1)
