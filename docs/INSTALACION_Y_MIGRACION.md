# Guía de instalación y migración (PetFun)

Esta guía explica cómo preparar el entorno, aplicar migraciones y poner datos de prueba para el proyecto PetFun.

## Requisitos

- Python 3.12
- pip
- PowerShell (Windows)
- Opcional: VS Code con la extensión de Python

## 1. Clonar el repositorio

```powershell
# Ajusta la URL si es privada
git clone <URL_DEL_REPO>
cd PetFun
```

## 2. Crear y activar entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la ejecución de scripts, habilita:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## 3. Instalar dependencias


Para este proyecto base con Django:
```powershell
pip install django==5.2.6
```

## 4. Configurar variables (desarrollo)

- `DEBUG` está activado por defecto.
- Base de datos SQLite lista por defecto (`db.sqlite3`).
- Soporte `.env`: el proyecto carga variables desde un archivo `.env` en la raíz (gracias a python-dotenv).

## 5. Migraciones (base de datos)

Si ya existe una base de datos previa y vas a cambiar de modelo de usuario, borra `db.sqlite3` antes de migrar:
```powershell
if (Test-Path .\db.sqlite3) { Remove-Item .\db.sqlite3 -Force }
```

Aplica migraciones desde cero:
```powershell
python manage.py migrate
```

Esto creará:
- Tablas del sistema (`auth`, `admin`, `sessions`, etc.).
- El modelo de usuario personalizado (`accounts.User`).
- Usuarios de prueba gracias a la migración `accounts/0002_seed_users.py`:
  - demo1@example.com / demo12345
  - demo2@example.com / demo12345

## 6. Crear superusuario (opcional)

```powershell
python manage.py createsuperuser
# Usa un email y contraseña propios
```

## 7. Ejecutar el servidor de desarrollo

```powershell
python manage.py runserver
```

- Home: http://127.0.0.1:8000/
- Login: http://127.0.0.1:8000/login/
- Registro: http://127.0.0.1:8000/register/
- Mi cuenta: http://127.0.0.1:8000/account/
- Admin: http://127.0.0.1:8000/admin/

## 8. Datos de prueba

- Usa los usuarios demo incluidos o crea nuevos desde `/register` o el panel `/admin`.
- En `/account/` puedes editar el perfil, cambiar contraseña y eliminar la cuenta (con confirmación por contraseña).

### Catálogo y filtros

- Catálogo: http://127.0.0.1:8000/catalog/
- Puedes filtrar por categoría padre y subcategoría con query string:
  - `?parent=<NombreCategoria>`
  - `?parent=<NombreCategoria>&sub=<NombreSubcategoria>`
  - Ejemplo: `/catalog/?parent=Juguetes%20para%20Perro&sub=Mordedores`
- En la home verás tarjetas por categoría con accesos rápidos a subcategorías.

### Checkout y cesta

- No se puede iniciar el checkout con la cesta vacía. Si intentas ir a pagar sin artículos, serás redirigido al inicio con un aviso.

## 9. Tests y cobertura

Ejecuta los tests con cobertura:
```powershell
python manage.py test
```

Si deseas cobertura detallada, puedes instalar `coverage` y ejecutarlo manualmente:
```powershell
pip install coverage
coverage run manage.py test
coverage html
# Abre htmlcov/index.html en tu navegador
```

## 10. Problemas comunes

- Error de migraciones inconsistentes tras cambiar `AUTH_USER_MODEL`:
  - Borra `db.sqlite3` y vuelve a `python manage.py migrate`.
- No puedo activar el entorno en PowerShell:
  - Revisa `Set-ExecutionPolicy` como arriba.
- No puedo iniciar sesión con email:
  - Asegúrate de que el usuario tenga el campo `email` rellenado y usa la contraseña correcta.

## 11. Pagos (Stripe) en desarrollo

Este proyecto integra un checkout en 3 pasos con Stripe. Para pruebas locales:

1) Instalar la librería de Stripe:
```powershell
pip install stripe
```

2) Configurar variables de entorno (opcional; si no se configuran, el flujo se simula sin cobro real):
```powershell
$env:STRIPE_SECRET_KEY = "sk_test_xxx"
$env:STRIPE_PUBLISHABLE_KEY = "pk_test_xxx"
```

3) Iniciar servidor y usar tarjetas de prueba de Stripe (p.ej. `4242 4242 4242 4242`).

Rutas relevantes:
- Inicio del checkout: `/orders/checkout/`
- Confirmación: `/orders/checkout/confirm/`

## 12. Uso de archivo .env

Para evitar configurar variables en cada sesión, puedes usar un archivo `.env`:

1) Instala la dependencia (una vez):
```powershell
pip install python-dotenv
```

2) Copia el ejemplo y edítalo:
```powershell
Copy-Item .env.example .env
```

3) Abre `.env` y ajusta valores (por ejemplo, claves de Stripe, SMTP, etc.).

Variables frecuentes en `.env`:
- `DEBUG=1`
- `STRIPE_SECRET_KEY=sk_test_xxx`
- `STRIPE_PUBLISHABLE_KEY=pk_test_xxx`
- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST=smtp.gmail.com` / `EMAIL_PORT=587` / `EMAIL_USE_TLS=1`
- `EMAIL_HOST_USER=tu_correo` / `EMAIL_HOST_PASSWORD=tu_password_o_app_password`
- `DEFAULT_FROM_EMAIL=no-reply@petfun.local`

El fichero `.env` ya está ignorado en `.gitignore`.
