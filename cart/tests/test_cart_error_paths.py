from __future__ import annotations

import json
from django.test import TestCase, Client
from django.urls import reverse


class CartErrorPathsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _post(self, name, payload):
        return self.client.post(reverse(f"cart:{name}"), data=json.dumps(payload), content_type="application/json")

    def test_add_with_invalid_product_returns_400(self):
        res = self._post("add", {"product_id": 9999, "quantity": 1})
        self.assertEqual(res.status_code, 400)

    def test_update_with_missing_fields_returns_400(self):
        res = self._post("update", {"product_id": None})
        self.assertEqual(res.status_code, 400)
