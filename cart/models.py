from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint

from catalog.models import Product


class Cart(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="carts"
	)
	session_key = models.CharField(max_length=40, unique=True, null=True, blank=True)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "carrito"
		verbose_name_plural = "carritos"

	def __str__(self) -> str:
		who = self.user.email if self.user_id else (self.session_key or "anónimo")
		return f"Carrito {self.pk} – {who}"

	def recalc_total(self, save: bool = True):
		total = sum(item.subtotal for item in self.items.all())
		self.total = total
		if save:
			self.save(update_fields=["total", "updated_at"])
		return total


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
	quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		verbose_name = "item de carrito"
		verbose_name_plural = "items de carrito"
		constraints = [
			CheckConstraint(check=Q(quantity__gte=1), name="cartitem_quantity_gte_1"),
			UniqueConstraint(fields=["cart", "product"], name="unique_cart_product"),
		]

	def save(self, *args, **kwargs):
		if not self.unit_price and self.product_id:
			self.unit_price = self.product.price
		self.subtotal = (self.unit_price or 0) * self.quantity
		super().save(*args, **kwargs)
		self.cart.recalc_total(save=True)

	def __str__(self) -> str:
		return f"{self.quantity} x {self.product.name}"

