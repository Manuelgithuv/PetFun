from __future__ import annotations

from django.test import TestCase
from django.urls import NoReverseMatch

from catalog.forms import CategoryForm, ProductForm, ManufacturerForm
from django.test import override_settings
from catalog.apps import _seed_catalog_if_empty
from catalog.models import Category, Manufacturer, Product


class CatalogFormsTests(TestCase):
    def test_category_form_parent_cannot_be_self(self):
        parent = Category.objects.create(name="Root")
        form = CategoryForm(instance=parent, data={"name": "Root", "parent": parent.id})
        self.assertFalse(form.is_valid())
        self.assertIn("padre", str(form.errors))

    def test_product_form_initialization_safe_when_reverse_missing(self):
        # No panel_* urls exist; ProductForm should still initialize without raising
        cat = Category.objects.create(name="Root")
        form = ProductForm()
        # manufacturer is optional and category/manufacturer queryset ordered
        self.assertIn("manufacturer", form.fields)
        self.assertFalse(form.fields["manufacturer"].required)

    def test_manufacturer_form_basic(self):
        form = ManufacturerForm(data={"name": "Brand", "description": "d"})
        self.assertTrue(form.is_valid())
        obj = form.save()
        self.assertEqual(obj.name, "Brand")


class CatalogAppSeedTests(TestCase):
    def test_seed_catalog_if_empty_populates_data(self):
        #self.assertFalse(Product.objects.exists())
        with override_settings(DEBUG=True):
            _seed_catalog_if_empty(sender=None)
        # Should have created categories, manufacturers and products
        self.assertTrue(Category.objects.exists())
        self.assertTrue(Manufacturer.objects.exists())
        self.assertTrue(Product.objects.exists())
