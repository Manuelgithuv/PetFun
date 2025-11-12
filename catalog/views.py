from django.db import models
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import render

from .models import Category, Product, Manufacturer


def catalog_home(request):
    """Catálogo con posibilidad de filtrar por categoría padre y subcategoría.

    Filtros por query string:
      - parent: nombre de la categoría padre (p.ej. "Perros")
      - sub: nombre de la subcategoría (p.ej. "Juguetes")
    """
    parent_name = request.GET.get('parent')
    sub_name = request.GET.get('sub')
    q = request.GET.get('q', '').strip()
    mfr = request.GET.get('manufacturer', '').strip()

    parents_qs = Category.objects.filter(parent__isnull=True).order_by('name')
    if parent_name:
        parents_qs = parents_qs.filter(name=parent_name)
    parents = list(parents_qs)

    subcats_by_parent = {}
    products_by_subcat = {}
    for parent in parents:
        subcats_qs = Category.objects.filter(parent=parent).order_by('name')
        if sub_name:
            subcats_qs = subcats_qs.filter(name=sub_name)
        subcats = []
        for sc in subcats_qs:
            prod_qs = Product.objects.filter(category=sc)
            if q:
                prod_qs = prod_qs.filter(
                    Q(name__icontains=q)
                    | Q(manufacturer__name__icontains=q)
                    | Q(category__name__icontains=q)
                    | Q(category__parent__name__icontains=q)
                )
            if mfr:
                prod_qs = prod_qs.filter(manufacturer__name=mfr)
            prods = list(prod_qs.order_by('name'))
            if prods:
                subcats.append(sc)
                products_by_subcat[sc.id] = prods
        subcats_by_parent[parent.id] = subcats

    ctx = {
        'categories': parents,
        'subcats_by_parent': subcats_by_parent,
        'products_by_subcat': products_by_subcat,
        'active_parent': parent_name or '',
        'active_sub': sub_name or '',
        'active_q': q,
        'active_manufacturer': mfr,
        'manufacturers': list(Manufacturer.objects.order_by('name').values_list('name', flat=True)),
    }
    return render(request, 'catalog/list.html', ctx)
