from django.test import TestCase
from django.urls import reverse


class HomeTests(TestCase):
	def test_homepage_renders(self):
		resp = self.client.get(reverse("home"))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "Productos destacados")

	def test_login_page_renders(self):
		resp = self.client.get(reverse("login"))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "Iniciar sesión")
