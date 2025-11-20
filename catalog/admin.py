from django.contrib import admin

from .models import Category, Manufacturer, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "parent")
	search_fields = ("name",)
	list_filter = ("parent",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
	list_display = ("id", "name")
	search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("id", "sku", "name", "category", "manufacturer", "price", "stock", "status")
	list_filter = ("category", "manufacturer", "status")
	search_fields = ("sku", "name", "manufacturer__name", "category__name")
	autocomplete_fields = ("category", "manufacturer")
	list_editable = ("price", "stock")

	actions = ("mark_out_of_stock", "mark_available")

	@admin.action(description="Marcar como agotado")
	def mark_out_of_stock(self, request, queryset):
		queryset.update(status="agotado")

	@admin.action(description="Marcar como disponible")
	def mark_available(self, request, queryset):
		queryset.update(status="disponible")

