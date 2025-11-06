from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
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
    ]
    for row in data:
        if not User.objects.filter(email=row['email']).exists():
            User.objects.create(**row)


def unseed_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(email__in=['demo1@example.com', 'demo2@example.com']).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_users, reverse_code=unseed_users),
    ]