from __future__ import annotations

import json
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from catalog.models import Category, Product


class CartApiTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.cat = Category.objects.create(name="Perros")
		self.sub = Category.objects.create(name="Juguetes", parent=self.cat)
		self.p = Product.objects.create(
			name="Mordedor",
			short_description="",
			description="",
			price=Decimal("9.99"),
			stock=3,
			category=self.sub,
			image_url="https://example.com/mordedor1.jpg",
			sku="",
		)

	def _post(self, url_name: str, payload: dict):
		url = reverse(f"cart:{url_name}")
		return self.client.post(url, data=json.dumps(payload), content_type="application/json")

	def test_add_to_cart_and_clamp_stock(self):
		r = self._post("add", {"product_id": self.p.id, "quantity": 2})
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertEqual(len(data["items"]), 1)
		self.assertEqual(data["items"][0]["quantity"], 2)

		r = self._post("add", {"product_id": self.p.id, "quantity": 5})
		self.assertEqual(r.status_code, 200)
		data = r.json()
		self.assertEqual(data["items"][0]["quantity"], 3)

	def test_update_quantity_and_remove(self):
		self._post("add", {"product_id": self.p.id, "quantity": 1})
		r = self._post("update", {"product_id": self.p.id, "quantity": 10})
		self.assertEqual(r.status_code, 200)
		self.assertEqual(r.json()["items"][0]["quantity"], 3)

		r = self._post("remove", {"product_id": self.p.id})
		self.assertEqual(r.status_code, 200)
		self.assertEqual(len(r.json()["items"]), 0)

	def test_add_out_of_stock_rejected(self):
		self.p.stock = 0
		self.p.save()
		r = self._post("add", {"product_id": self.p.id, "quantity": 1})
		self.assertEqual(r.status_code, 400)
