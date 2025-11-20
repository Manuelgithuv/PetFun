from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from catalog.models import Product, Category


@require_http_methods(["GET"])
def home(request):
	"""Home con productos destacados y subcategorías navegables."""
	qs = Product.objects.order_by("-created_at").all()[:6]
	products = list(qs)
	parents = Category.objects.filter(parent__isnull=True).order_by('name')
	subcats_by_parent = {}
	for p in parents:
		subs = Category.objects.filter(parent=p).order_by('name')
		subcats_by_parent[p.name] = list(subs.values_list('name', flat=True))
	return render(request, "home.html", {"products": products, "subcats_by_parent": subcats_by_parent})


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


