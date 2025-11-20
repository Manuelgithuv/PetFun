from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings
from django.contrib.auth.hashers import make_password


def _seed_users_if_empty(sender, **kwargs):
    if not getattr(settings, 'DEBUG', True):
        return
    try:
        from accounts.models import User
        if User.objects.exists():
            return
        data = [
            dict(
                email='demo1@example.com',
                first_name='Demo',
                last_name='Uno',
                phone='600111222',
                address='Calle Falsa 123',
                city='Madrid',
                postal_code='28001',
                password=make_password('demo12345'),
                is_active=True,
            ),
            dict(
                email='demo2@example.com',
                first_name='Demo',
                last_name='Dos',
                phone='600333444',
                address='Av. Principal 456',
                city='Barcelona',
                postal_code='08001',
                password=make_password('demo12345'),
                is_active=True,
            ),
            dict(
                email='admin@petfun.local',
                first_name='Admin',
                last_name='PetFun',
                phone='600000000',
                address='Calle Admin 1',
                city='Madrid',
                postal_code='28000',
                password=make_password('Admin12345!'),
                is_active=True,
                is_staff=True,
                is_superuser=True,
            ),
        ]
        for row in data:
            if not User.objects.filter(email=row['email']).exists():
                User.objects.create(**row)
    except Exception:
        pass


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    def ready(self) -> None:
        post_migrate.connect(_seed_users_if_empty, sender=self)
        return super().ready()
