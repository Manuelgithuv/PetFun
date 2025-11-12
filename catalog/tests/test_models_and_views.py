from __future__ import annotations

from django.test import TestCase, Client
from django.urls import reverse

from catalog.models import Category, Manufacturer, Product


class CatalogModelsTests(TestCase):
	def setUp(self):
		self.parent = Category.objects.create(name="Perros")
		self.sub = Category.objects.create(name="Juguetes", parent=self.parent)
		self.mfr = Manufacturer.objects.create(name="Acme")

	def test_product_save_sets_status_and_sku(self):
		p = Product.objects.create(
			name="Hueso",
			short_description="Delicioso",
			description="Un hueso para perros",
			price=10,
			stock=3,
			category=self.sub,
			manufacturer=self.mfr,
			image_url="https://example.com/hueso.jpg",
			sku="",
		)
		self.assertTrue(p.sku)
		self.assertEqual(p.status, Product.Status.AVAILABLE)

		p.stock = 0
		p.save()
		self.assertEqual(p.status, Product.Status.SOLD_OUT)

	def test_str_methods(self):
		self.assertEqual(str(self.parent), "Perros")
		self.assertEqual(str(self.mfr), "Acme")
		p = Product.objects.create(
			name="Peluche",
			short_description="",
			description="",
			price=5,
			stock=1,
			category=self.sub,
			image_url="https://example.com/peluche.jpg",
			sku="",
		)
		self.assertIn("Peluche", str(p))


class CatalogViewTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.parent = Category.objects.create(name="Perros")
		self.sub1 = Category.objects.create(name="Juguetes", parent=self.parent)
		self.sub2 = Category.objects.create(name="Comida", parent=self.parent)
		self.m1 = Manufacturer.objects.create(name="Acme")
		self.m2 = Manufacturer.objects.create(name="PetsCo")
		Product.objects.create(
			name="Mordedor fuerte",
			short_description="",
			description="",
			price=12,
			stock=5,
			category=self.sub1,
			manufacturer=self.m1,
			image_url="https://example.com/mordedor.jpg",
			sku="",
		)
		Product.objects.create(
			name="Pienso premium",
			short_description="",
			description="",
			price=30,
			stock=2,
			category=self.sub2,
			manufacturer=self.m2,
			image_url="https://example.com/pienso.jpg",
			sku="",
		)

	def test_catalog_filters_by_parent_and_search(self):
		url = reverse("catalog:home") + "?parent=Perros&q=Juguetes"
		res = self.client.get(url)
		self.assertEqual(res.status_code, 200)
		self.assertIn("products_by_subcat", res.context)
		self.assertTrue(res.context["products_by_subcat"])  # at least one subcat with products

	def test_catalog_filters_by_manufacturer(self):
		url = reverse("catalog:home") + "?parent=Perros&manufacturer=Acme"
		res = self.client.get(url)
		self.assertContains(res, "Mordedor fuerte")
		self.assertNotContains(res, "Pienso premium")


class CategorySeedTests(TestCase):
	fixtures = []

	def test_seed_categories_exist(self):
		from catalog.apps import _seed_catalog_if_empty
		from django.test import override_settings
		with override_settings(DEBUG=True):
			_seed_catalog_if_empty(sender=None)
		roots = set(Category.objects.filter(parent__isnull=True).values_list("name", flat=True))
		self.assertTrue({"Juguetes para Perro", "Juguetes para Gato"}.issubset(roots))
		perro = Category.objects.get(name="Juguetes para Perro")
		sub_names = set(perro.children.values_list("name", flat=True))
		expected = {"Mordedores", "Pelotas", "De inteligencia", "Peluches"}
		self.assertTrue(expected.issubset(sub_names))
