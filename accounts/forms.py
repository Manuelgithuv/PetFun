from django import forms
from django.contrib.auth import get_user_model
import re


User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Repetir contraseña")

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "postal_code",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean_first_name(self):
        name = (self.cleaned_data.get("first_name") or "").strip()
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        if any(ch.isdigit() for ch in name):
            raise forms.ValidationError("El nombre no puede contener números.")
        if not re.fullmatch(r"[\wÀ-ÖØ-öø-ÿ'\-\s]+", name, flags=re.UNICODE):
            raise forms.ValidationError("El nombre contiene caracteres no válidos.")
        return name

    def clean_last_name(self):
        name = (self.cleaned_data.get("last_name") or "").strip()
        if not name:
            raise forms.ValidationError("Los apellidos son obligatorios.")
        if any(ch.isdigit() for ch in name):
            raise forms.ValidationError("Los apellidos no pueden contener números.")
        if not re.fullmatch(r"[\wÀ-ÖØ-öø-ÿ'\-\s]+", name, flags=re.UNICODE):
            raise forms.ValidationError("Los apellidos contienen caracteres no válidos.")
        return name

    def clean_phone(self):
        raw = (self.cleaned_data.get("phone") or "").strip()
        # Normalize by removing spaces, dashes and parentheses
        normalized = re.sub(r"[\s\-()]+", "", raw)
        # Accept optional leading + and 9-15 digits overall
        if not re.fullmatch(r"\+?\d{9,15}", normalized):
            raise forms.ValidationError("Introduce un número de teléfono válido (9-15 dígitos, opcional '+').")
        return normalized

    def clean_postal_code(self):
        cp = (self.cleaned_data.get("postal_code") or "").strip()
        # España: 5 dígitos
        if not re.fullmatch(r"\d{5}", cp):
            raise forms.ValidationError("Introduce un código postal válido de 5 dígitos.")
        return cp

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "postal_code",
        ]

    def clean_first_name(self):
        name = (self.cleaned_data.get("first_name") or "").strip()
        if not name:
            raise forms.ValidationError("El nombre es obligatorio.")
        if any(ch.isdigit() for ch in name):
            raise forms.ValidationError("El nombre no puede contener números.")
        if not re.fullmatch(r"[\wÀ-ÖØ-öø-ÿ'\-\s]+", name, flags=re.UNICODE):
            raise forms.ValidationError("El nombre contiene caracteres no válidos.")
        return name

    def clean_last_name(self):
        name = (self.cleaned_data.get("last_name") or "").strip()
        if not name:
            raise forms.ValidationError("Los apellidos son obligatorios.")
        if any(ch.isdigit() for ch in name):
            raise forms.ValidationError("Los apellidos no pueden contener números.")
        if not re.fullmatch(r"[\wÀ-ÖØ-öø-ÿ'\-\s]+", name, flags=re.UNICODE):
            raise forms.ValidationError("Los apellidos contienen caracteres no válidos.")
        return name

    def clean_phone(self):
        raw = (self.cleaned_data.get("phone") or "").strip()
        normalized = re.sub(r"[\s\-()]+", "", raw)
        if not re.fullmatch(r"\+?\d{9,15}", normalized):
            raise forms.ValidationError("Introduce un número de teléfono válido (9-15 dígitos, opcional '+').")
        return normalized

    def clean_postal_code(self):
        cp = (self.cleaned_data.get("postal_code") or "").strip()
        if not re.fullmatch(r"\d{5}", cp):
            raise forms.ValidationError("Introduce un código postal válido de 5 dígitos.")
        return cp