from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("account/delete/", views.account_delete, name="account_delete"),
]