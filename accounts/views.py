from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm, ProfileForm


@require_http_methods(["GET", "POST"])
def register(request):
	if request.method == "POST":
		form = RegisterForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Cuenta creada con éxito. ¡Bienvenido/a!")
			return redirect("account")
	else:
		form = RegisterForm()
	return render(request, "register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def account(request):
	user = request.user
	profile_form = ProfileForm(instance=user)
	pwd_form = PasswordChangeForm(user)

	if request.method == "POST":
		if "submit_profile" in request.POST:
			profile_form = ProfileForm(request.POST, instance=user)
			if profile_form.is_valid():
				profile_form.save()
				messages.success(request, "Perfil actualizado correctamente.")
				return redirect("account")
		elif "submit_password" in request.POST:
			pwd_form = PasswordChangeForm(user, request.POST)
			if pwd_form.is_valid():
				user = pwd_form.save()
				update_session_auth_hash(request, user)
				messages.success(request, "Contraseña actualizada correctamente.")
				return redirect("account")

	return render(request, "account.html", {"form": profile_form, "pwd_form": pwd_form})


@login_required
@require_http_methods(["POST"])
def account_delete(request):
	# Confirm with current password to prevent accidental or forged deletes
	pwd = request.POST.get("password", "")
	user = request.user
	if not pwd or not user.check_password(pwd):
		messages.error(request, "Contraseña incorrecta para eliminar la cuenta.")
		return redirect("account")

	email = user.email
	user.delete()
	logout(request)
	messages.success(request, f"La cuenta {email} ha sido eliminada.")
	return redirect("home")
