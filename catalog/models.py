from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils import timezone

import secrets
import string


class Category(models.Model):
	name = models.CharField(max_length=150, unique=True)
	image_url = models.URLField(blank=True, null=True)
	parent = models.ForeignKey(
		"self", related_name="children", on_delete=models.CASCADE, blank=True, null=True
	)

	class Meta:
		verbose_name = "categoría"
		verbose_name_plural = "categorías"

	def __str__(self) -> str:
		return self.name


class Manufacturer(models.Model):
	name = models.CharField(max_length=150, unique=True)
	description = models.TextField(blank=True)

	class Meta:
		verbose_name = "fabricante"
		verbose_name_plural = "fabricantes"

	def __str__(self) -> str:
		return self.name


class Product(models.Model):
	class Status(models.TextChoices):
		AVAILABLE = "disponible", "Disponible"
		SOLD_OUT = "agotado", "Agotado"

	sku = models.CharField(max_length=32, unique=True, db_index=True)
	name = models.CharField(max_length=200)
	short_description = models.CharField(max_length=300, blank=True)
	description = models.TextField()
	price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
	stock = models.PositiveIntegerField(validators=[MinValueValidator(0)])
	category = models.ForeignKey('catalog.Category', on_delete=models.PROTECT, related_name="products")
	manufacturer = models.ForeignKey(
		'catalog.Manufacturer', on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
	)
	image = models.ImageField(upload_to='products/', blank=True, null=True)

	status = models.CharField(
		max_length=12,
		choices=Status.choices,
		default=Status.AVAILABLE,
		db_index=True,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "producto"
		verbose_name_plural = "productos"
		constraints = [
			CheckConstraint(check=Q(stock__gte=0), name="product_stock_gte_0"),
		]

	def save(self, *args, **kwargs):
		self.status = self.Status.SOLD_OUT if self.stock == 0 else self.Status.AVAILABLE
		if not self.sku:
			self.sku = self._generate_unique_sku()
		super().save(*args, **kwargs)

	@classmethod
	def _generate_unique_sku(cls) -> str:
		alphabet = string.ascii_uppercase + string.digits
		while True:
			candidate = "PF-" + "".join(secrets.choice(alphabet) for _ in range(8))
			if not cls.objects.filter(sku=candidate).exists():
				return candidate

	def __str__(self) -> str:
		return f"{self.name} ({self.sku})"

