from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from authentication.models import DestinataireNotification
from feedback.models import FeedbackReport

User = get_user_model()


class FeedbackSubmitTests(TestCase):
    def setUp(self):
        from django.core.cache import caches

        caches["ratelimit"].clear()
        self.user = User.objects.create_user(
            username="agent@example.test",
            email="agent@example.test",
            password="Mot-de-passe-test-2026!",
        )
        self.url = reverse("feedback:submit")

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.post(
            self.url,
            {"type": "bug", "page_declaree": "/", "message": "Un bug visible ici."},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        self.assertEqual(FeedbackReport.objects.count(), 0)

    def test_authenticated_json_creates_report_and_sends_email(self):
        DestinataireNotification.objects.create(email="gestion@example.test")
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "type": "bug",
                "page_declaree": "/structures/",
                "message": "La carte ne s'affiche plus depuis hier.",
                "page_contexte": "/structures/",
            },
            HTTP_REFERER="http://testserver/structures/",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        report = FeedbackReport.objects.get()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.page_declaree, "/structures/")
        self.assertEqual(report.page_auto, "/structures/")
        self.assertEqual(report.statut, FeedbackReport.STATUT_NOUVEAU)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Nouveau signalement", mail.outbox[0].subject)
        self.assertIn("gestion@example.test", mail.outbox[0].to)

    def test_page_declaree_remains_editable_when_different_from_detected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "type": "suggestion",
                "page_declaree": "/dashboard/",
                "message": "Ajouter un filtre par commune serait utile.",
            },
            HTTP_REFERER="http://testserver/structures/",
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 201)
        report = FeedbackReport.objects.get()
        self.assertEqual(report.page_declaree, "/dashboard/")
        self.assertEqual(report.page_auto, "/structures/")

    def test_message_too_short_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {"type": "bug", "page_declaree": "/", "message": "court"},
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(FeedbackReport.objects.count(), 0)

    def test_classic_post_redirects_with_success_message(self):
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {
                "type": "autre",
                "page_declaree": "/",
                "message": "Simple remarque sur la page d'accueil du site.",
                "next": "/",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FeedbackReport.objects.count(), 1)

    def test_email_failure_does_not_lose_report(self):
        DestinataireNotification.objects.create(email="gestion@example.test")
        self.client.force_login(self.user)
        with self.assertLogs("feedback.views", level="ERROR"):
            with __import__("unittest.mock", fromlist=["patch"]).patch(
                "feedback.views.notify_admins_new_feedback",
                side_effect=RuntimeError("SMTP down"),
            ):
                response = self.client.post(
                    self.url,
                    {
                        "type": "bug",
                        "page_declaree": "/",
                        "message": "Bug malgré email en panne volontairement.",
                    },
                    HTTP_ACCEPT="application/json",
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest",
                )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FeedbackReport.objects.count(), 1)
