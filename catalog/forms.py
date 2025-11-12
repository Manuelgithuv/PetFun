from __future__ import annotations

from django import forms

from .models import Category, Product, Manufacturer


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "image_url", "parent"]

    def clean_parent(self):
        parent = self.cleaned_data.get("parent")
        if parent and getattr(self.instance, "pk", None) and parent.pk == self.instance.pk:
            raise forms.ValidationError("La categoría padre no puede ser la misma categoría.")
        return parent


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Excluir campos gestionados automáticamente
        exclude = ["sku", "status", "created_at", "updated_at"]
        widgets = {
            "short_description": forms.TextInput(attrs={"maxlength": 300}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar opciones para facilitar selección
        if "category" in self.fields:
            self.fields["category"].queryset = Category.objects.order_by("name")
        if "manufacturer" in self.fields:
            self.fields["manufacturer"].queryset = Manufacturer.objects.order_by("name")
            self.fields["manufacturer"].required = False
        # Ayuda con enlaces para crear rápidamente
        try:
            from django.urls import reverse

            self.fields["category"].help_text = (
                f"¿No encuentras la categoría? "
                f"<a href='{reverse('panel_category_create')}' target='_blank'>Crear categoría</a>"
            )
            self.fields["manufacturer"].help_text = (
                f"¿No encuentras el fabricante? "
                f"<a href='{reverse('panel_manufacturer_create')}' target='_blank'>Crear fabricante</a>"
            )
        except Exception:
            # Si aún no están cargadas las URLs, omitimos los enlaces sin romper el formulario
            pass


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ["name", "description"]
