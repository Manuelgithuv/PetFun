from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings


def _seed_orders_if_empty(sender, **kwargs):
    if not getattr(settings, 'DEBUG', True):
        return
    try:
        from decimal import Decimal
        import random
        from orders.models import Order, OrderItem
        from catalog.models import Product

        if Order.objects.exists():
            return
        products = list(Product.objects.all()[:20])
        if not products:
            return
        statuses = ['recibido', 'procesando', 'enviado', 'entregado', 'cancelado']
        for i in range(12):
            total = Decimal('0.00')
            order = Order.objects.create(
                user=None,
                contact_email=f"demo-tracking-{i}@example.com",
                total=Decimal('0.00'),
                status=random.choice(statuses),
                tracking_code=f"PT-DEMO-{i:03d}",
                ship_name=f"Cliente {i}",
                ship_street=f"Calle Demo {i}",
                ship_number=str(10 + i),
                ship_floor='',
                ship_city='Ciudad',
                ship_postal_code=f"28{100 + i}",
                ship_country='ES',
                payment_method='tarjeta',
            )
            for _ in range(random.randint(1, 3)):
                p = random.choice(products)
                qty = random.randint(1, 3)
                unit = p.price
                subtotal = unit * qty
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    quantity=qty,
                    unit_price=unit,
                    subtotal=subtotal,
                )
                total += subtotal
            order.total = total
            order.save(update_fields=['total'])
    except Exception:
        pass


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"
    def ready(self) -> None:
        post_migrate.connect(_seed_orders_if_empty, sender=self)
        return super().ready()
