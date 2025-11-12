from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "tracking_code", "user", "contact_email", "status", "total", "created_at")
	search_fields = ("tracking_code", "contact_email", "user__email")
	list_filter = ("status", "payment_method")
	inlines = [OrderItemInline]

