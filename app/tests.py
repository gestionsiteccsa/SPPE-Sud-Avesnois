import re

from django.core.cache import caches
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import bad_request, permission_denied, server_error


class ContentSecurityPolicyTests(TestCase):
    def test_application_pages_emit_strict_csp(self):
        response = self.client.get(reverse("login"))

        self.assertIn("Content-Security-Policy", response)
        policy = response["Content-Security-Policy"]
        self.assertIn("script-src 'self' 'nonce-", policy)
        script_src = next(
            directive
            for directive in policy.split(";")
            if directive.strip().startswith("script-src")
        )
        self.assertNotIn("unsafe-inline", script_src)
        self.assertNotIn("unsafe-eval", policy)
        self.assertIn("frame-ancestors 'none'", policy)

    def test_inline_scripts_carry_the_response_nonce(self):
        response = self.client.get(reverse("login"))

        policy = response["Content-Security-Policy"]
        match = re.search(r"'nonce-([A-Za-z0-9_-]+)'", policy)
        self.assertIsNotNone(match)
        self.assertContains(response, f'nonce="{match.group(1)}"', html=False)

    def test_admin_has_csp_with_relaxed_scripts_only(self):
        response = self.client.get(reverse("admin:login"))

        self.assertIn("Content-Security-Policy", response)
        policy = response["Content-Security-Policy"]
        script_src = next(
            directive
            for directive in policy.split(";")
            if directive.strip().startswith("script-src")
        )
        self.assertIn("unsafe-inline", script_src)
        self.assertNotIn("unsafe-eval", policy)
        self.assertIn("frame-ancestors 'none'", policy)
        self.assertIn("object-src 'none'", policy)


class SearchEngineBlockingTests(TestCase):
    def test_robots_txt_disallows_all(self):
        response = self.client.get(reverse("robots"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "Disallow: /")

    def test_pages_carry_noindex_header(self):
        response = self.client.get(reverse("login"))

        self.assertIn("X-Robots-Tag", response)
        self.assertIn("noindex", response["X-Robots-Tag"])
        self.assertIn("nofollow", response["X-Robots-Tag"])

    def test_admin_pages_carry_noindex_header(self):
        response = self.client.get(reverse("admin:login"))

        self.assertIn("X-Robots-Tag", response)
        self.assertIn("noindex", response["X-Robots-Tag"])

    def test_pages_carry_noindex_meta(self):
        response = self.client.get(reverse("login"))

        self.assertContains(
            response, '<meta name="robots" content="noindex, nofollow">', html=True
        )


class AdminRateLimitTests(TestCase):
    def setUp(self):
        caches["ratelimit"].clear()

    def test_admin_login_is_rate_limited_per_account(self):
        url = reverse("admin:login")

        for _attempt in range(10):
            response = self.client.post(
                url,
                {"username": "cible@example.test", "password": "incorrect"},
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {"username": "cible@example.test", "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 403)

    def test_another_account_is_not_blocked_by_same_ip(self):
        url = reverse("admin:login")

        for _attempt in range(10):
            self.client.post(
                url,
                {"username": "cible@example.test", "password": "incorrect"},
            )

        response = self.client.post(
            url,
            {"username": "autre@example.test", "password": "incorrect"},
        )

        self.assertEqual(response.status_code, 200)


class SecurityHeadersTests(TestCase):
    def test_clickjacking_protection_is_always_active(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response["X-Frame-Options"], "DENY")

    @override_settings(
        IS_PRODUCTION=True,
        SECURE_SSL_REDIRECT=False,
        SECURE_CONTENT_TYPE_NOSNIFF=True,
        SECURE_HSTS_SECONDS=3600,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=False,
        SECURE_HSTS_PRELOAD=False,
    )
    def test_production_security_headers(self):
        response = Client().get(reverse("login"), secure=True)

        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["Strict-Transport-Security"], "max-age=3600")


class CustomErrorPagesTests(TestCase):
    def test_404_uses_custom_template(self):
        with override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
            response = self.client.get("/chemin-qui-nexiste-pas/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Page introuvable", status_code=404)

    def test_403_uses_custom_template(self):
        response = permission_denied(RequestFactory().get("/"), None)

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Accès refusé", status_code=403)

    def test_400_uses_custom_template(self):
        response = bad_request(RequestFactory().get("/"), Exception("Requête suspecte"))

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Requête invalide", status_code=400)

    def test_500_uses_custom_template(self):
        with override_settings(DEBUG=False):
            response = server_error(RequestFactory().get("/"))

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Une erreur interne est survenue", status_code=500)
