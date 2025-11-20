from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product
from django.utils import timezone
import secrets
import string


class Order(models.Model):
	class Status(models.TextChoices):
		RECEIVED = "recibido", "Recibido"
		PROCESSING = "procesando", "Procesando"
		SHIPPED = "enviado", "Enviado"
		DELIVERED = "entregado", "Entregado"
		CANCELED = "cancelado", "Cancelado"

	class PaymentMethod(models.TextChoices):
		CARD = "tarjeta", "Tarjeta"
		TRANSFER = "transferencia", "Transferencia"

	tracking_code = models.CharField(max_length=20, unique=True, db_index=True)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
	)
	contact_email = models.EmailField()
	total = models.DecimalField(max_digits=12, decimal_places=2)
	status = models.CharField(
		max_length=12, choices=Status.choices, default=Status.RECEIVED, db_index=True
	)

	# Shipping address
	ship_name = models.CharField(max_length=150)
	ship_street = models.CharField(max_length=200)
	ship_number = models.CharField(max_length=30)
	ship_floor = models.CharField(max_length=30, blank=True)
	ship_city = models.CharField(max_length=100)
	ship_postal_code = models.CharField(max_length=20)
	ship_country = models.CharField(max_length=100)

	payment_method = models.CharField(
		max_length=15, choices=PaymentMethod.choices
	)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Pedido {self.tracking_code} ({self.get_status_display()})"

	def save(self, *args, **kwargs):
		if not self.tracking_code:
			self.tracking_code = self._generate_tracking_code()
		super().save(*args, **kwargs)

	@staticmethod
	def _generate_tracking_code() -> str:
		alphabet = string.ascii_uppercase + string.digits
		prefix = timezone.now().strftime("PT-%Y%m-")
		for _ in range(5):
			code = prefix + "".join(secrets.choice(alphabet) for _ in range(8))
			if not Order.objects.filter(tracking_code=code).exists():
				return code
		return prefix + secrets.token_hex(6).upper()


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
	product_name = models.CharField(max_length=200)
	quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	subtotal = models.DecimalField(max_digits=12, decimal_places=2)

	def save(self, *args, **kwargs):
		if not self.product_name and self.product_id:
			self.product_name = self.product.name
		if not self.unit_price and self.product_id:
			self.unit_price = self.product.price
		self.subtotal = (self.unit_price or 0) * self.quantity
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return f"{self.quantity} x {self.product_name}"

