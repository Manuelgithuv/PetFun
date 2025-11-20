from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_start, name='checkout_start'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('track/', views.track_order, name='track_order'),
]
