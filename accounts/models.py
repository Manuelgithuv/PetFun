from django.db import models
from django.contrib.auth.models import (
	AbstractBaseUser,
	PermissionsMixin,
	BaseUserManager,
)
from django.utils import timezone


class UserManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError("El email es obligatorio")
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_active", True)
		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")
		return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField("email address", unique=True)
	first_name = models.CharField(max_length=150, blank=False)
	last_name = models.CharField(max_length=150, blank=False)
	phone = models.CharField(max_length=30, blank=False)
	address = models.CharField(max_length=255, blank=False)
	city = models.CharField(max_length=100, blank=False)
	postal_code = models.CharField(max_length=20, blank=False)

	# Meta/flags
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(default=timezone.now)
	created_at = models.DateTimeField(auto_now_add=True)

	objects = UserManager()

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS: list[str] = []

	class Meta:
		verbose_name = "usuario"
		verbose_name_plural = "usuarios"

	def __str__(self) -> str:
		full = f"{self.first_name} {self.last_name}".strip()
		return full or self.email

