from __future__ import annotations

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from cart.context_processors import cart as cart_ctx
from cart.utils import get_or_create_cart


class CartUtilsAndContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.User = get_user_model()

    def test_get_or_create_cart_anonymous_creates_session_cart(self):
        req = self.factory.get("/")
        # Attach session
        from django.contrib.sessions.middleware import SessionMiddleware

        SessionMiddleware(lambda r: None).process_request(req)
        req.session.save()
        req.user = AnonymousUser()

        cart = get_or_create_cart(req)
        self.assertIsNotNone(cart.session_key)
        self.assertIsNone(cart.user_id)

    def test_get_or_create_cart_authenticated_uses_user_cart(self):
        user = self.User.objects.create_user(email="u@example.com", password="x")
        req = self.factory.get("/")
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware

        SessionMiddleware(lambda r: None).process_request(req)
        req.session.save()
        req.user = user

        cart = get_or_create_cart(req)
        self.assertEqual(cart.user_id, user.id)
        self.assertTrue(cart.session_key)

    def test_cart_context_processor_returns_counts(self):
        req = self.factory.get("/")
        from django.contrib.sessions.middleware import SessionMiddleware

        SessionMiddleware(lambda r: None).process_request(req)
        req.session.save()
        ctx = cart_ctx(req)
        self.assertIn("cart", ctx)
        self.assertIn("cart_item_count", ctx)
        self.assertEqual(ctx["cart_item_count"], 0)
