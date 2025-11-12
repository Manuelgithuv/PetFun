from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from decimal import Decimal
import stripe
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse

from cart.utils import get_or_create_cart
from cart.models import Cart
from catalog.models import Product
from .models import Order, OrderItem

@require_http_methods(["GET"])
def checkout_start(request):
	"""Step 1: show catalog shortcut or summary with proceed button."""
	cart = get_or_create_cart(request)
	if not cart.items.exists():
		messages.error(request, "Tu cesta está vacía. Añade productos antes de ir a pagar.")
		return redirect('home')
	return render(request, 'orders/checkout_start.html', {
		'cart': cart,
	})

@require_http_methods(["GET", "POST"])
def checkout_payment(request):
	"""Step 2: shipping info + create Stripe PaymentIntent."""
	cart = get_or_create_cart(request)
	if not cart.items.exists():
		messages.error(request, "Tu cesta está vacía. Añade productos antes de ir a pagar.")
		return redirect('home')
	if request.method == 'POST':
		email = request.POST.get('email')
		payment_method = Order.PaymentMethod.CARD
		ship = {
			'name': request.POST.get('ship_name'),
			'street': request.POST.get('ship_street'),
			'number': request.POST.get('ship_number'),
			'floor': request.POST.get('ship_floor',''),
			'city': request.POST.get('ship_city'),
			'postal_code': request.POST.get('ship_postal_code'),
			'country': request.POST.get('ship_country'),
		}

		amount = int(Decimal(cart.total) * 100)
		client_secret = None
		payment_intent_id = None
		is_card = bool(settings.STRIPE_SECRET_KEY)
		if is_card:
			stripe.api_key = settings.STRIPE_SECRET_KEY
			intent = stripe.PaymentIntent.create(
				amount=amount,
				currency='eur',
				capture_method='manual',
				automatic_payment_methods={'enabled': True},
				metadata={'cart_id': str(cart.id)},
			)
			client_secret = intent.client_secret
			payment_intent_id = intent.id
		else:
			messages.error(request, "Stripe no está configurado. Añade STRIPE_SECRET_KEY y STRIPE_PUBLISHABLE_KEY en .env para pagar con tarjeta.")
			return render(request, 'orders/checkout_payment.html', {
				'cart': cart,
				'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
				'initial': {},
			})

		# Persist checkout data in session for the confirm step
		request.session['checkout_email'] = email
		request.session['checkout_ship'] = ship
		request.session['checkout_payment_method'] = payment_method
		request.session['payment_intent_id'] = payment_intent_id

		# Render the payment element to collect card details
		return render(request, 'orders/checkout_payment.html', {
			'cart': cart,
			'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
			'initial': {},
			'stripe_client_secret': client_secret,
			'stripe_return_url': request.build_absolute_uri(reverse('orders:checkout_confirm')),
		})
	initial = {}
	if request.user.is_authenticated:
		u = request.user
		full_name = f"{getattr(u, 'first_name', '')} {getattr(u, 'last_name', '')}".strip()
		initial = {
			'email': getattr(u, 'email', ''),
			'ship_name': full_name,
			'ship_street': getattr(u, 'address', ''),
			'ship_number': '',
			'ship_floor': '',
			'ship_city': getattr(u, 'city', ''),
			'ship_postal_code': getattr(u, 'postal_code', ''),
			'ship_country': 'ES',
		}
	return render(request, 'orders/checkout_payment.html', {
		'cart': cart,
		'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
		'initial': initial,
	})

@require_http_methods(["GET"]) 
def checkout_confirm(request):
	"""Step 3: confirmation, create order and clear cart (simulated immediate success)."""
	cart = get_or_create_cart(request)
	if not cart.items.exists():
		messages.error(request, "Tu cesta está vacía. Añade productos antes de ir a pagar.")
		return redirect('home')
	email = request.session.get('checkout_email')
	ship = request.session.get('checkout_ship') or {}
	pi = request.session.get('payment_intent_id')
	pay_method = request.session.get('checkout_payment_method') or Order.PaymentMethod.CARD

	if not email or not ship:
		return redirect('orders:checkout_payment')

	# If paying by card, verify PaymentIntent state and amount
	if pay_method == Order.PaymentMethod.CARD and settings.STRIPE_SECRET_KEY:
		if not pi:
			messages.error(request, "No se encontró la sesión de pago de Stripe. Vuelve a introducir el pago.")
			return redirect('orders:checkout_payment')
		try:
			stripe.api_key = settings.STRIPE_SECRET_KEY
			pi_obj = stripe.PaymentIntent.retrieve(pi)
		except Exception:
			messages.error(request, "No se pudo verificar el pago en Stripe. Inténtalo de nuevo.")
			return redirect('orders:checkout_payment')
		expected_amount = int(Decimal(cart.total) * 100)
		if int(pi_obj.get('amount', 0)) != expected_amount:
			messages.error(request, "El importe del pago no coincide con el carrito. Vuelve a confirmar el pago.")
			return redirect('orders:checkout_payment')
		status = pi_obj.get('status')
		if status not in ('succeeded', 'requires_capture'):
			messages.error(request, f"El pago no está listo (estado: {status}). Completa la autenticación o inténtalo de nuevo.")
			return redirect('orders:checkout_payment')

	
	with transaction.atomic():
		
		cart_items = list(cart.items.select_related('product'))
		product_ids = [it.product_id for it in cart_items]
		products_locked = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}
		adjustments = []
		for it in cart_items:
			p = products_locked.get(it.product_id)
			if not p:
				it.delete()
				adjustments.append(f"Se eliminó '{it.product_name or 'producto'}' (ya no disponible)")
				continue
			if p.stock <= 0:
				it.delete()
				adjustments.append(f"Se eliminó '{p.name}' (sin stock)")
				continue
			if it.quantity > p.stock:
				old_q = it.quantity
				it.quantity = p.stock
				it.unit_price = p.price
				it.save()
				adjustments.append(f"Se ajustó '{p.name}' de {old_q} → {p.stock} por stock disponible")
			else:
				it.unit_price = p.price
				it.save()

		cart.recalc_total()

		if adjustments:
			if not cart.items.exists():
				messages.error(request, "Algunos productos ya no están disponibles. Tu cesta ha quedado vacía.")
			else:
				messages.error(request, "Actualizamos tu cesta por cambios de stock/precio: " + "; ".join(adjustments))
			return redirect('orders:checkout_start')

		# For card payments with manual capture: capture now after validating stock
		if pay_method == Order.PaymentMethod.CARD and settings.STRIPE_SECRET_KEY:
			try:
				stripe.api_key = settings.STRIPE_SECRET_KEY
				current_pi = stripe.PaymentIntent.retrieve(request.session.get('payment_intent_id'))
				if current_pi.get('status') == 'requires_capture':
					stripe.PaymentIntent.capture(current_pi['id'])
				elif current_pi.get('status') != 'succeeded':
					messages.error(request, f"El pago no está listo para finalizar (estado: {current_pi.get('status')}).")
					return redirect('orders:checkout_payment')
			except Exception:
				messages.error(request, "No se pudo capturar el pago en Stripe. Inténtalo de nuevo.")
				return redirect('orders:checkout_payment')
		order = Order.objects.create(
			user=request.user if request.user.is_authenticated else None,
			contact_email=email,
			total=cart.total,
			status=Order.Status.RECEIVED,
			ship_name=ship.get('name',''),
			ship_street=ship.get('street',''),
			ship_number=ship.get('number',''),
			ship_floor=ship.get('floor',''),
			ship_city=ship.get('city',''),
			ship_postal_code=ship.get('postal_code',''),
			ship_country=ship.get('country',''),
			payment_method=pay_method,
		)
		for it in cart.items.select_related('product').all():
			p = products_locked[it.product_id]
			# Final guard: if somehow stock changed, abort
			if it.quantity > p.stock:
				messages.error(request, f"Stock insuficiente para '{p.name}'. Inténtalo de nuevo.")
				return redirect('orders:checkout_start')
			OrderItem.objects.create(
				order=order,
				product=p,
				product_name=p.name,
				quantity=it.quantity,
				unit_price=it.unit_price,
				subtotal=it.subtotal,
			)
			p.stock = max(0, p.stock - it.quantity)
			p.save()

		cart.items.all().delete()
		cart.recalc_total()

	for k in ['checkout_email','checkout_ship','payment_intent_id','checkout_payment_method']:
		request.session.pop(k, None)

	try:
		body = (
			f"Gracias por tu compra!\n\n"
			f"Código de seguimiento: {order.tracking_code}\n"
			f"Importe: {order.total} €\n"
			f"Envío a: {order.ship_name}, {order.ship_street} {order.ship_number}, {order.ship_city} {order.ship_postal_code}, {order.ship_country}\n\n"
			"Detalles:\n" + "\n".join([f"- {it.quantity} x {it.product_name} = {it.subtotal} €" for it in order.items.all()])
		)
		send_mail(
			"Confirmación de pedido PetFun",
			body,
			settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@petfun.local',
			[order.contact_email],
			fail_silently=not settings.DEBUG,
		)
	except Exception:
		pass

	return render(request, 'orders/checkout_confirm.html', {
		'order': order,
	})

@require_http_methods(["GET", "POST"])
def track_order(request):
	"""Public order tracking by tracking_code."""
	code = ""
	order = None
	if request.method == 'POST':
		code = (request.POST.get('code') or '').strip()
		if code:
			order = Order.objects.filter(tracking_code=code).first()
			if not order:
				messages.error(request, "No se ha encontrado ningún pedido con ese código.")
	return render(request, 'orders/track.html', {"order": order, "code": code})
