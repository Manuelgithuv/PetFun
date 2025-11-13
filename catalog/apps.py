from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings


def _seed_catalog_if_empty(sender, **kwargs):
    # Only seed in DEBUG to avoid polluting real environments
    if not getattr(settings, 'DEBUG', True):
        return
    try:
        from decimal import Decimal
        from catalog.models import Category, Manufacturer, Product
        import re

        # If products already exist, upgrade simple placeholder images to descriptive ones
        if Product.objects.exists():
            for p in Product.objects.all():
                if p.image_url and re.fullmatch(r"https://placehold\.co/600x400\?text=[A-Z0-9\-]+", p.image_url):
                    new_url = f"https://placehold.co/600x400?text={p.sku}+{p.name.replace(' ', '+')}"
                    if p.image_url != new_url:
                        p.image_url = new_url
                        p.save(update_fields=["image_url"])
            return

        # Categories
        structure = {
            'Juguetes para Perro': [
                'Mordedores', 'Pelotas', 'De inteligencia', 'Peluches'
            ],
            'Juguetes para Gato': [
                'Ratones de juguete', 'Caña', 'Hierba gatera', 'Túneles'
            ],
        }
        for parent_name, children in structure.items():
            parent, _ = Category.objects.get_or_create(name=parent_name, defaults={})
            for child in children:
                Category.objects.get_or_create(name=child, parent=parent, defaults={})

        # Manufacturers
        mfr_names = ['PetMaster', 'FelineJoy', 'CaninePlay', 'CatCraft']
        mfr_map = {}
        for name in mfr_names:
            m, _ = Manufacturer.objects.get_or_create(name=name, defaults={})
            mfr_map[name] = m

        def subcat(name, parent):
            return Category.objects.filter(name=name, parent__name=parent).first()

        perro = 'Juguetes para Perro'
        gato = 'Juguetes para Gato'

        targets = {
            'DOG-MOR-001': (perro, 'Mordedores', 'Mordedor resistente', Decimal('7.99'), 25, 'PetMaster'),
            'DOG-MOR-002': (perro, 'Mordedores', 'Mordedor con sabor', Decimal('8.50'), 18, 'CaninePlay'),
            'DOG-PEL-001': (perro, 'Pelotas', 'Pelota rebotadora', Decimal('5.49'), 40, 'CaninePlay'),
            'DOG-INT-001': (perro, 'De inteligencia', 'Puzzle canino nivel 1', Decimal('19.90'), 10, 'PetMaster'),
            'DOG-PELUC-001': (perro, 'Peluches', 'Peluchito con sonido', Decimal('12.00'), 12, 'CaninePlay'),
            'CAT-RAT-001': (gato, 'Ratones de juguete', 'Ratón de fieltro', Decimal('3.99'), 50, 'FelineJoy'),
            'CAT-CAN-001': (gato, 'Caña', 'Caña con plumas', Decimal('6.99'), 35, 'CatCraft'),
            'CAT-HIER-001': (gato, 'Hierba gatera', 'Hierba gatera premium', Decimal('4.50'), 60, 'FelineJoy'),
            'CAT-TUN-001': (gato, 'Túneles', 'Túnel plegable', Decimal('14.99'), 14, 'CatCraft'),
        }
        for sku, (parent_name, sub_name, name, price, stock, mfr_name) in targets.items():
            cat = subcat(sub_name, parent_name)
            if not cat:
                continue
            Product.objects.get_or_create(
                sku=sku,
                defaults=dict(
                    name=name,
                    short_description='',
                    description=f"{name} para {parent_name.lower()}.",
                    price=price,
                    stock=stock,
                    category=cat,
                    manufacturer=mfr_map.get(mfr_name),
                    image_url=f"https://placehold.co/600x400?text={sku}+{name.replace(' ', '+')}",
                )
            )

        # Extra rows
        m_pet = mfr_map['PetMaster']
        m_can = mfr_map['CaninePlay']
        m_fel = mfr_map['FelineJoy']
        m_cat = mfr_map['CatCraft']
        rows = [
            ('DOG-MOR-003', perro, 'Mordedores', 'Mordedor dental', Decimal('6.50'), 30, m_pet),
            ('DOG-MOR-004', perro, 'Mordedores', 'Mordedor cuerda', Decimal('7.20'), 22, m_can),
            ('DOG-PEL-002', perro, 'Pelotas', 'Pelota luminosa', Decimal('6.90'), 28, m_can),
            ('DOG-PEL-003', perro, 'Pelotas', 'Pelota resistente XL', Decimal('8.90'), 15, m_pet),
            ('DOG-INT-002', perro, 'De inteligencia', 'Puzzle canino nivel 2', Decimal('24.90'), 8, m_pet),
            ('DOG-PELUC-002', perro, 'Peluches', 'Peluche sin relleno', Decimal('10.50'), 18, m_can),
            ('CAT-RAT-002', gato, 'Ratones de juguete', 'Ratón con catnip', Decimal('4.20'), 45, m_fel),
            ('CAT-RAT-003', gato, 'Ratones de juguete', 'Set de 3 ratones', Decimal('6.80'), 32, m_cat),
            ('CAT-CAN-002', gato, 'Caña', 'Caña telescópica', Decimal('7.99'), 20, m_cat),
            ('CAT-HIER-002', gato, 'Hierba gatera', 'Spray catnip', Decimal('5.20'), 26, m_fel),
            ('CAT-TUN-002', gato, 'Túneles', 'Túnel con ventana', Decimal('16.50'), 12, m_cat),
        ]
        for sku, parent_name, sub_name, name, price, stock, mfr in rows:
            cat = subcat(sub_name, parent_name)
            if not cat:
                continue
            Product.objects.get_or_create(
                sku=sku,
                defaults=dict(
                    name=name,
                    short_description='',
                    description=f"{name} para {parent_name.lower()}.",
                    price=price,
                    stock=stock,
                    category=cat,
                    manufacturer=mfr,
                    image_url=f"https://placehold.co/600x400?text={sku}+{name.replace(' ', '+')}",
                )
            )
    except Exception:
        # Never block app startup in dev due to seeding
        pass


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self) -> None:
        post_migrate.connect(_seed_catalog_if_empty, sender=self)
        return super().ready()
