# Guía de despliegue de proyecto (PetFun)

Esta guía explica cómo desplegar el proyecto PetFun.

## Requisitos

- Tener una cuenta creada en [pythonanywhere](https://www.pythonanywhere.com)

## 1. Abrir un terminal / consola de comandos

Vaya al apartado Consoles → Bash. Tras hacer este paso, se encontrara en una página parecida a esta:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso1.png)

Esta consola permanecera abierta siempre y cuando no la borre, esta se encuentra de forma más accesible en el apartado Dashboard

## 2. Clonar el repositorio

Tras esto, procedemos a clonar el repositorio de git:

```powershell
git clone https://github.com/Manuelgithuv/PetFun.git
```

y ejecutamos el comando "ls" para comprobar que se ha descargado correctamente:

```powershell
ls
```

Debería de quedar la consola tal que:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso2.png)

## 3. Crear un entorno virtual

Creamos un entorno virtual mediante el comando:

```powershell
mkvirtualenv --python=/usr/bin/python3.12 .venv
```

Tras esto, en la propia terminal se verá como se ha activado el entorno creado:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso3.png)

## 4. Intalar las dependencias

Nos metemos dentro del proyecto y instalamos todas las dependencias necesarias establecidas en el archivo requirements.txt:

```powershell
cd PetFun
pip install -r requirements.txt
```

Tras esto, en la propia terminal se verá como se han instalado todas las dependencias necesarias:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso4.png)

## 5. Configurar el “Web app” en PythonAnywhere

Seleccione las barras de la esquina superior derecha y vaya al apartado "Web"

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso5_1.png)

Ahora en esta pantalla clickee en el apartado "Add a new web app"

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso5_1.png)

En esta pantalla se abrirá un panel, pulse el boton "Next". Tras esto, el panel cambiará y ahora tendra que seleccionar la opción "Manual configuration". Después clickee en "Python 3.12" y tras esto en "Next".

Tras esto se creara la web "[tu usuario].pythonanywhere.com".

En la sección de Virtualenv de esa web app, indique la ruta de su virtualenv (/home/tu usuario/.virtualenvs/.venv) y guárdalo.

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso5_2.png)

Debería de quedar algo tal que así:

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso5_3.png)

## 6. Editar el archivo WSGI para apuntar a tu proyecto

Desde la propia pestaña Web, haga clic en el enlace del archivo WSGI configuration file (algo como /var/www/tuusuario_pythonanywhere_com_wsgi.py). Abra el editor.

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso5_3.png) 
<!-- Esta es la misma imagen que la anterior para mostrar que la sección es la de justo arriba de Virtualenv -->

Borre lo que haya en el archivo y ponga. **OJO, donde ponga "tuusuario" ponga su nombre de usuario, si no, no funcionara**:

```powershell
# +++++++++++ DJANGO +++++++++++
import os
import sys

path = '/home/tuusuario/PetFun'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'petfun.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

```

Dentro del archivo modificado con  mi nombre de usuario queda un archivo tal que:

![Pantalla de Web](imagenes_docs/PantallaDeWSGI.png) 

Como puede ver en la imagen ahora pulse en el boton de guardar "Save".

## 7. Establecer los archivos estáticos del proyecto.

Vuelva a darle a las tres barras horizontales (en la esquina superior derecha) y vaya a "Files". Entre en PetFun/ → petfun/ → settings.py.

En la línea 52 encontrara "ALLOWED_HOSTS" cambie esa línea completa por esta. **OJO, donde ponga "tuusuario" ponga su nombre de usuario, si no, no funcionara**:

```powershell
ALLOWED_HOSTS = ['tuusuario.pythonanywhere.com']
```

Justo debajo aparece las variables: 

```powershell
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

Pues copie este código ponga justo abajo.  **OJO, donde ponga "tuusuario" ponga su nombre de usuario, si no, no funcionara**:

```powershell
STATIC_URL = '/static/'

STATIC_ROOT = '/home/tuusuario/PetFun/staticfiles'

STATICFILES_DIRS = [
    '/home/tuusuario/PetFun/media/products',
]
```
El archivo tiene queda, en mi caso, tal que:

![Pantalla de Settings](imagenes_docs/PantallaDeSettings.png)

Tras esto, guarde los cambios (boton "Save") y en las tres barras horizontales, vaya a "Web" y vaya al apartado de "Virtualenv" para abrir la terminal con el entorno virtual activado:

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso5_3.png) 
<!-- Esta imagen se ha usado para enseñar que se puede abrir la maquina virtual con el .venv desde ahi-->

Deberia de salir esta terminal:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso7_1.png)

Entonces copie en la terminal. Esto lo que hará es crear la carpeta staticfiles **OJO, donde ponga "tuusuario" ponga su nombre de usuario, si no, no funcionara**:

```powershell
mkdir /home/tuusuario/PetFun/staticfiles
```

En mi caso:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso7_2.png)

Y por último, ejece este comando para copiar los archivos de una carpeta a otra.

```powershell
workon venv
cd ~/PetFun
python manage.py collectstatic
```

Debería quedar algo tal que:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso7_3.png)


## 8. Realizar las migraciones.

Para realizar las migraciones solo tiene que usar el comando:

```powershell
python manage.py migrate
```

El terminal debería de quedar como se muestra a continuación:

![Pantalla de Shell](imagenes_docs/PantallaDeShellPaso8.png)


## 9. Establecer el .env.

Vuelva a darle a las tres barras horizontales (en la esquina superior derecha) y vaya a "Files" para acto seguido ir a PetFun/.

Dentro tiene que crear el archivo vacío ".env"

![Pantalla de Files](imagenes_docs/PantallaDeFilesPaso9_1.png)

Metase dentro del archivo y pegue lo siguiente:

```powershell
DEBUG=1
ALLOWED_HOSTS='josemamg.pythonanywhere.com'
SECRET_KEY=change-me

STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=pk_test_51SSkv3JfoY0bVIIdPwIeMBGflhjE8LOlC05L2LLOtKhz6BFywynE9B1h0kkkjgS7zmnBckDcPZ52TIbBEVvfhMaY00JrZyb6Ed

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
EMAIL_HOST_USER=noreply.petfun@gmail.com
EMAIL_HOST_PASSWORD=fdat lszp oapy nntl
DEFAULT_FROM_EMAIL=noreply.petfun@gmail.com
```

Debería de quedar tal que:

![Pantalla de Files](imagenes_docs/PantallaDeFilesPaso9_1.png)

Después guardelo.


## 10. Establecer la ruta de archivos a usar y listo.

Vaya a la sección "Web" mediante el icono de las líneas horizontales y busque la sección "Static files"

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso10_1.png)

En esta tiene que poner de URL = /static/  y Directory = /home/tuusuario/PetFun/staticfiles. **OJO, donde ponga "tuusuario" ponga su nombre de usuario, si no, no funcionara**

En mi caso sería:

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso10_2.png)

Y por último, recargar el dominio (boton "reload").

![Pantalla de Web](imagenes_docs/PantallaDeWebPaso10_3.png)

Y listo, ¡ya estaría PetFun funcionando en su dominio personal! 

![Pantalla de PetFun](imagenes_docs/PantallaDePetFun.png)