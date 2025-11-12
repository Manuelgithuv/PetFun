from __future__ import annotations

from django.test import TestCase, override_settings

from accounts.apps import _seed_users_if_empty
from django.contrib.auth import get_user_model


class AccountsAppSeedTests(TestCase):
    def test_seed_users_if_empty_creates_demo_users(self):
        User = get_user_model()
        # Ensure empty
        User.objects.all().delete()
        with override_settings(DEBUG=True):
            _seed_users_if_empty(sender=None)
        emails = set(User.objects.values_list("email", flat=True))
        self.assertIn("demo1@example.com", emails)
        self.assertIn("demo2@example.com", emails)
        self.assertIn("admin@petfun.local", emails)
