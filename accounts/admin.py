from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	ordering = ("-date_joined",)
	list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
	search_fields = ("email", "first_name", "last_name")
	readonly_fields = ("date_joined", "last_login", "created_at")

	fieldsets = (
		(None, {"fields": ("email", "password")}),
		(_("Información personal"), {
			"fields": ("first_name", "last_name", "phone", "address", "city", "postal_code"),
		}),
		(_("Permisos"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
		(_("Fechas"), {"fields": ("last_login", "date_joined", "created_at")}),
	)

	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "password1", "password2", "is_staff", "is_superuser", "is_active"),
		}),
	)

# Register your models here.
