from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsFlowTests(TestCase):
    def setUp(self):
        self.password = "demo12345"
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password=self.password,
        )

    def test_register_get(self):
        resp = self.client.get(reverse("register"))
        self.assertEqual(resp.status_code, 200)

    def test_register_post_creates_and_logs_in(self):
        payload = {
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "phone": "600000000",
            "address": "Calle 1",
            "city": "Madrid",
            "postal_code": "28000",
            "password": "StrongPass1",
            "password2": "StrongPass1",
        }
        resp = self.client.post(reverse("register"), data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertContains(resp, "Mi cuenta")

    def test_register_duplicate_email_error(self):
        # Existing email
        payload = {
            "email": self.user.email,
            "first_name": "X",
            "last_name": "Y",
            "phone": "600000000",
            "address": "Calle 2",
            "city": "Sevilla",
            "postal_code": "41001",
            "password": "StrongPass1",
            "password2": "StrongPass1",
        }
        resp = self.client.post(reverse("register"), data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Ya existe un usuario con ese email.")

    def test_register_password_mismatch_error(self):
        payload = {
            "email": "mismatch@example.com",
            "first_name": "A",
            "last_name": "B",
            "phone": "600000001",
            "address": "Calle 3",
            "city": "Valencia",
            "postal_code": "46001",
            "password": "StrongPass1",
            "password2": "StrongPass2",
        }
        resp = self.client.post(reverse("register"), data=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Las contraseñas no coinciden.")

    def test_login_with_email_ok(self):
        resp = self.client.post(reverse("login"), data={"email": self.user.email, "password": self.password})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("home"))

    def test_login_redirect_next_safe(self):
        resp = self.client.post(
            reverse("login") + "?next=" + reverse("account"),
            data={"email": self.user.email, "password": self.password},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("account"))

    def test_login_with_email_invalid(self):
        resp = self.client.post(reverse("login"), data={"email": self.user.email, "password": "badpass"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "incorrectos")

    def test_account_edit_profile(self):
        self.client.login(email=self.user.email, password=self.password)
        payload = {
            "submit_profile": "1",
            "first_name": "NuevoNombre",
            "last_name": self.user.last_name,
            "phone": "611111111",
            "address": "Otra 123",
            "city": "BCN",
            "postal_code": "08000",
        }
        resp = self.client.post(reverse("account"), data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NuevoNombre")
        self.assertContains(resp, "Perfil actualizado correctamente")

    def test_account_change_password(self):
        self.client.login(email=self.user.email, password=self.password)
        payload = {
            "submit_password": "1",
            "old_password": self.password,
            "new_password1": "NuevaPass1",
            "new_password2": "NuevaPass1",
        }
        resp = self.client.post(reverse("account"), data=payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.client.logout()
        ok = self.client.login(email=self.user.email, password="NuevaPass1")
        self.assertTrue(ok)

    def test_account_delete_requires_password(self):
        self.client.login(email=self.user.email, password=self.password)
        resp = self.client.post(reverse("account_delete"), data={"password": "bad"}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
        self.assertContains(resp, "Contraseña incorrecta")
        resp = self.client.post(reverse("account_delete"), data={"password": self.password}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())

    def test_login_next_open_redirect_blocked(self):
        resp = self.client.post(
            reverse("login") + "?next=http://evil.com/",
            data={"email": self.user.email, "password": self.password},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("home"))

    def test_logout_redirects_home(self):
        self.client.login(email=self.user.email, password=self.password)
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("home"))

    def test_user_manager_validations_and_str(self):
        # create_user requires email
        with self.assertRaisesMessage(ValueError, "El email es obligatorio"):
            User.objects.create_user(email=None, password="x")

        # create_superuser requires flags
        with self.assertRaisesMessage(ValueError, "is_staff=True"):
            User.objects.create_superuser(email="super1@example.com", password="x", is_staff=False)
        with self.assertRaisesMessage(ValueError, "is_superuser=True"):
            User.objects.create_superuser(email="super2@example.com", password="x", is_superuser=False)

        su = User.objects.create_superuser(email="super3@example.com", password="x")
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)

        # __str__ uses name when present, otherwise email
        u = User.objects.create_user(email="noname@example.com", password="x")
        self.assertEqual(str(u), "noname@example.com")
        u.first_name = "Ana"; u.last_name = "García"; u.save()
        self.assertEqual(str(u), "Ana García")
