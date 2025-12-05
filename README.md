<div style="display: flex; align-items: center; gap: 20px;">
  <img src="Images/Logo.png" alt="PetFun Logo" width="150" style="flex-shrink: 0;">
</div>

#

Una plataforma de comercio electrónico basada en Django para juguetes para mascotas. PetFun permite a los usuarios explorar un catálogo de productos para mascotas, gestionar carritos de compra, procesar pagos seguros a través de Stripe y rastrear sus pedidos.

- 🌐 Web del proyecto: https://josemamg.pythonanywhere.com  
- 📄 Guía de instalación local: [`docs/INSTALACION_Y_MIGRACION.md`](docs/INSTALACION_Y_MIGRACION_Y_MIGRACION.md)  
- 🚀 Guía de despliegue: [`docs/3.14 INSTRUCCIONES_PARA_DESPLIEGUE V1.md`](docs/3.14%20INSTRUCCIONES_PARA_DESPLIEGUE%20V1.md)


## Estructura del Proyecto

```
petfun/                   # Configuración principal del proyecto Django
├── settings.py           # Configuración del proyecto
├── urls.py               # Enrutamiento de URLs principal
└── wsgi.py               # Aplicación WSGI

accounts/                 # Autenticación de usuario y gestión de cuenta
├── models.py             # Modelo de Usuario personalizado
├── views.py              # Vistas de autenticación (login, registro, perfil)
├── forms.py              # Formularios de autenticación
└── tests/                # Pruebas de autenticación

catalog/                  # Gestión del catálogo de productos
├── models.py             # Modelos de Producto y Categoría
├── views.py              # Vistas del catálogo
└── tests/                # Pruebas del catálogo

cart/                     # Funcionalidad del carrito de compra
├── models.py             # Modelos del carrito
├── views.py              # Vistas de gestión del carrito
├── context_processors.py # Contexto del carrito para plantillas
└── tests/                # Pruebas del carrito

orders/                   # Sistema de pedidos y pago
├── models.py             # Modelos de Pedidos
├── views.py              # Vistas de pago y pedidos
└── tests/                # Pruebas de pago y pedidos

core/                     # Funcionalidad principal
├── views.py              # Vistas de inicio y principales
└── tests/                # Pruebas principales

templates/                # Plantillas HTML
└── catalog/              # Plantillas de productos
orders/                   # Plantillas de pago

media/                    # Cargas de usuarios (productos, etc.)
```