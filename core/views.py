from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def home(request):
	"""Attractive storefront homepage with featured products."""
	products = [
		{
			"name": "Cama Ortopédica",
			"price": 39.99,
			"image": "https://images.unsplash.com/photo-1601758064135-0c3b3f2c9b74?w=800&q=80&auto=format&fit=crop",
		},
		{
			"name": "Juguete Mordedor",
			"price": 9.49,
			"image": "https://images.unsplash.com/photo-1593134257782-e89567b7718d?w=800&q=80&auto=format&fit=crop",
		},
		{
			"name": "Rascador Deluxe",
			"price": 54.90,
			"image": "https://images.unsplash.com/photo-1555169062-013468b47731?w=800&q=80&auto=format&fit=crop",
		},
		{
			"name": "Comedero Inteligente",
			"price": 79.00,
			"image": "https://images.unsplash.com/photo-1596495578065-6d1e3b2c9b65?w=800&q=80&auto=format&fit=crop",
		},
		{
			"name": "Arnés Reflectante",
			"price": 18.75,
			"image": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&q=80&auto=format&fit=crop",
		},
		{
			"name": "Fuente de Agua",
			"price": 29.95,
			"image": "https://images.unsplash.com/photo-1568640347023-a616a30bc3bd?w=800&q=80&auto=format&fit=crop",
		},
	]
	return render(request, "home.html", {"products": products})


@require_http_methods(["GET", "POST"])
def login_view(request):
	"""Login using email + password, with `next` redirect support."""
	if request.method == "POST":
		email = request.POST.get("email", "").strip()
		password = request.POST.get("password", "")

		User = get_user_model()
		user = None
		if email:
			u = User.objects.filter(email__iexact=email).order_by("id").first()
			if u is not None:
				user = authenticate(request, username=u.get_username(), password=password)

		if user is not None:
			login(request, user)
			messages.success(request, "¡Bienvenido/a de nuevo!")
			nxt = request.POST.get("next") or request.GET.get("next")
			if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
				return redirect(nxt)
			return redirect("home")
		else:
			messages.error(request, "Email o contraseña incorrectos.")

	ctx = {"next": request.GET.get("next", "")}
	return render(request, "login.html", ctx)


@require_http_methods(["POST", "GET"])
def logout_view(request):
	"""Log out the user and redirect to home."""
	if request.user.is_authenticated:
		logout(request)
		messages.success(request, "Has cerrado sesión.")
	return redirect("home")
