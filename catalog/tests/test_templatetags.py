from __future__ import annotations

from django.test import TestCase
from catalog.templatetags.catalog_extras import get_item


class TemplateTagsTests(TestCase):
    def test_get_item_ok_and_fallback(self):
        d = {"a": [1, 2]}
        self.assertEqual(get_item(d, "a"), [1, 2])
        # Non-mapping should not raise
        self.assertEqual(get_item(None, "a"), [])
