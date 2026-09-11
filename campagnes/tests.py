import hashlib
from datetime import date, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import caches
from django.db import transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from campagnes.models import (
    UpdateCampaign,
    UpdateRequest,
    UpdateRequestField,
    VerificationInvitation,
)
from campagnes.services import campaign as campagnes_emails
from campagnes.services.campaign import (
    CampaignError,
    campaign_stats,
    close_campaign,
    create_assisted_request,
    generate_letters,
    go_live,
    launch_campaign,
    remind_unanswered,
    review_request,
    submit_confirmation,
    submit_modification,
)
from campagnes.forms import UpdateCampaignForm
from authentication.models import UserCommune
from communes.models import Commune
from structures.models import AuditLog, Structure, TypeStructure

User = get_user_model()

PASSWORD = "Un-mot-de-passe-tres-long-2026"


def _make_campaign(**kwargs):
    defaults = {
        "name": "Campagne annuelle 2027",
        "starts_at": date.today(),
        "ends_at": date.today() + timedelta(days=30),
    }
    defaults.update(kwargs)
    return UpdateCampaign.objects.create(**defaults)


def _make_am(nom, prenom, *, email="", telephone="", commune=None):
    return Structure.objects.create(
        nom=nom,
        prenom=prenom,
        email=email,
        telephone=telephone,
        commune=commune,
        type=TypeStructure.objects.get_or_create(nom="Assistante maternelle")[0],
    )


class CampaignLifecycleTests(TestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.avec_email = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.sans_email = _make_am("Martin", "Léa", telephone="06 12 34 56 78", commune=self.commune)
        self.creche = Structure.objects.create(
            nom_structure="Crèche Les Lutins",
            type=TypeStructure.objects.get_or_create(nom="Micro-crèche")[0],
            commune=self.commune,
        )

    def test_launch_creates_invitations_only_for_assistantes_maternelles(self):
        campaign = _make_campaign()
        count = launch_campaign(campaign)

        self.assertEqual(count, 2)
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_OPEN)
        self.assertEqual(campaign.invitations.count(), 2)

    def test_launch_assigns_channels_and_sends_emails(self):
        campaign = _make_campaign()
        launch_campaign(campaign)

        email_invitation = campaign.invitations.get(structure=self.avec_email)
        letter_invitation = campaign.invitations.get(structure=self.sans_email)
        self.assertEqual(
            email_invitation.delivery_channel, VerificationInvitation.CHANNEL_EMAIL
        )
        self.assertEqual(email_invitation.status, VerificationInvitation.STATUS_SENT)
        self.assertIsNotNone(email_invitation.sent_at)
        self.assertEqual(
            letter_invitation.delivery_channel, VerificationInvitation.CHANNEL_LETTER
        )
        self.assertEqual(
            letter_invitation.status, VerificationInvitation.STATUS_NOT_CONTACTED
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["marie@example.test"])
        self.assertIn("Aucun compte n'est nécessaire", mail.outbox[0].body)
        self.assertIn("/verification/", mail.outbox[0].body)
        self.assertIn(campaign.ends_at.strftime("%d/%m/%Y"), mail.outbox[0].body)

    def test_cannot_launch_twice(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        with self.assertRaises(CampaignError):
            launch_campaign(campaign)

    def test_cannot_launch_before_start_date(self):
        campaign = _make_campaign(
            starts_at=date.today() + timedelta(days=7),
            ends_at=date.today() + timedelta(days=37),
        )
        with self.assertRaises(CampaignError):
            launch_campaign(campaign)
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_DRAFT)
        self.assertEqual(campaign.invitations.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_cannot_launch_after_end_date(self):
        campaign = _make_campaign(
            starts_at=date.today() - timedelta(days=30),
            ends_at=date.today() - timedelta(days=1),
        )
        with self.assertRaises(CampaignError):
            launch_campaign(campaign)
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_DRAFT)
        self.assertEqual(campaign.invitations.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_launch_keeps_error_status_when_email_fails(self):
        campaign = _make_campaign()

        def failing_send(invitation, raw_token, recipients):
            raise RuntimeError("SMTP indisponible")

        with mock.patch.object(
            campagnes_emails, "send_verification_invitation_email", failing_send
        ):
            launch_campaign(campaign)

        email_invitation = campaign.invitations.get(structure=self.avec_email)
        self.assertEqual(email_invitation.status, VerificationInvitation.STATUS_SEND_ERROR)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_OPEN)


class CampaignEmailTransactionTests(TransactionTestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.avec_email = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.sans_email = _make_am("Martin", "Léa", telephone="06 12 34 56 78", commune=self.commune)

    def test_launch_sends_emails_outside_the_database_transaction(self):
        campaign = _make_campaign()
        events = []
        real_send = campagnes_emails.send_verification_invitation_email

        def spy(invitation, raw_token, recipients):
            events.append(transaction.get_connection().in_atomic_block)
            return real_send(invitation, raw_token, recipients)

        with mock.patch.object(campagnes_emails, "send_verification_invitation_email", spy):
            launch_campaign(campaign)

        self.assertTrue(events)
        self.assertFalse(any(events))

    def test_remind_sends_emails_outside_the_database_transaction(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        events = []
        real_send = campagnes_emails.send_verification_invitation_email

        def spy(invitation, raw_token, recipients):
            events.append(transaction.get_connection().in_atomic_block)
            return real_send(invitation, raw_token, recipients)

        with mock.patch.object(campagnes_emails, "send_verification_invitation_email", spy):
            remind_unanswered(campaign)

        self.assertTrue(events)
        self.assertFalse(any(events))

    def test_go_live_sends_emails_outside_the_database_transaction(self):
        campaign = _make_campaign(test_mode=True, test_emails="test@example.test")
        launch_campaign(campaign)
        events = []
        real_send = campagnes_emails.send_verification_invitation_email

        def spy(invitation, raw_token, recipients):
            events.append(transaction.get_connection().in_atomic_block)
            return real_send(invitation, raw_token, recipients)

        with mock.patch.object(campagnes_emails, "send_verification_invitation_email", spy):
            go_live(campaign)

        self.assertTrue(events)
        self.assertFalse(any(events))

    def test_token_hash_stored_not_raw(self):
        campaign = _make_campaign()
        invitation, raw_token = VerificationInvitation.create_with_token(
            campaign, self.avec_email
        )
        expected_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        self.assertEqual(invitation.token_hash, expected_hash)
        self.assertNotEqual(invitation.token_hash, raw_token)
        self.assertFalse(
            VerificationInvitation.objects.filter(token_hash=raw_token).exists()
        )
        self.assertEqual(VerificationInvitation.find_by_token(raw_token), invitation)

    def test_close_marks_unanswered_expired(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        submit_confirmation(
            campaign.invitations.get(structure=self.avec_email),
            VerificationInvitation.CHANNEL_EMAIL,
        )
        expired = close_campaign(campaign)

        self.assertEqual(expired, 1)
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_CLOSED)
        self.assertEqual(
            campaign.invitations.get(structure=self.sans_email).status,
            VerificationInvitation.STATUS_EXPIRED,
        )
        self.assertEqual(
            campaign.invitations.get(structure=self.avec_email).status,
            VerificationInvitation.STATUS_CONFIRMED,
        )

    def test_remind_only_unanswered(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        submit_confirmation(
            campaign.invitations.get(structure=self.avec_email),
            VerificationInvitation.CHANNEL_EMAIL,
        )
        mail.outbox.clear()
        reminded = remind_unanswered(campaign)

        self.assertEqual(reminded, 1)
        self.assertEqual(len(mail.outbox), 0)  # sans e-mail → pas d'envoi
        letter = campaign.invitations.get(structure=self.sans_email)
        self.assertEqual(letter.status, VerificationInvitation.STATUS_SEND_SCHEDULED)

    def test_remind_issues_a_new_token_for_email(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        invitation = campaign.invitations.get(structure=self.avec_email)
        old_hash = invitation.token_hash
        mail.outbox.clear()
        remind_unanswered(campaign)
        invitation.refresh_from_db()
        self.assertNotEqual(invitation.token_hash, old_hash)
        self.assertEqual(len(mail.outbox), 1)

    def test_letters_generate_new_tokens_each_time(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        batch1 = generate_letters(campaign)
        batch2 = generate_letters(campaign)

        self.assertEqual(len(batch1), 1)
        self.assertEqual(len(batch2), 1)
        invitation, raw1 = batch1[0]
        _, raw2 = batch2[0]
        self.assertNotEqual(raw1, raw2)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, VerificationInvitation.STATUS_SEND_SCHEDULED)

    def test_stats(self):
        campaign = _make_campaign()
        launch_campaign(campaign)
        before = campaign_stats(campaign)
        self.assertEqual(before["total"], 2)
        self.assertEqual(before["sent"], 1)
        self.assertEqual(before["without_email"], 1)
        self.assertEqual(before["unanswered"], 2)

        submit_confirmation(
            campaign.invitations.get(structure=self.avec_email),
            VerificationInvitation.CHANNEL_EMAIL,
        )
        stats = campaign_stats(campaign)

        self.assertEqual(stats["confirmed"], 1)
        self.assertEqual(stats["responded"], 1)
        self.assertEqual(stats["unanswered"], 1)
        self.assertEqual(stats["response_rate"], 50.0)


class VerificationPublicPageTests(TestCase):
    def setUp(self):
        caches["ratelimit"].clear()
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.lea = _make_am("Martin", "Léa", email="lea@example.test", commune=self.commune)
        self.campaign = _make_campaign(status=UpdateCampaign.STATUS_OPEN)
        self.invitation, self.raw_token = VerificationInvitation.create_with_token(
            self.campaign, self.marie
        )
        self.url = reverse("campagnes:verification", kwargs={"token": self.raw_token})

    def test_page_shows_only_own_fiche(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dupont Marie")
        self.assertNotContains(response, "Martin Léa")

    def test_opening_is_recorded(self):
        self.client.get(self.url)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.opened_count, 1)
        self.assertEqual(self.invitation.status, VerificationInvitation.STATUS_OPENED)
        self.assertIsNotNone(self.invitation.opened_at)

    def test_unknown_token_returns_404(self):
        response = self.client.get(
            reverse("campagnes:verification", kwargs={"token": "token-inconnu"})
        )
        self.assertEqual(response.status_code, 404)

    def test_token_invalid_outside_period(self):
        old = _make_campaign(
            name="Ancienne",
            starts_at=date.today() - timedelta(days=60),
            ends_at=date.today() - timedelta(days=30),
            status=UpdateCampaign.STATUS_OPEN,
        )
        _, raw_token = VerificationInvitation.create_with_token(old, self.marie)
        response = self.client.get(
            reverse("campagnes:verification", kwargs={"token": raw_token})
        )
        self.assertEqual(response.status_code, 404)

    def test_token_invalid_when_campaign_not_open(self):
        draft = _make_campaign(name="Brouillon", status=UpdateCampaign.STATUS_DRAFT)
        _, raw_token = VerificationInvitation.create_with_token(draft, self.marie)
        response = self.client.get(
            reverse("campagnes:verification", kwargs={"token": raw_token})
        )
        self.assertEqual(response.status_code, 404)

    def test_confirm_sets_status_and_creates_request(self):
        response = self.client.post(self.url, {"action": "confirmer"})

        self.assertContains(response, "Merci")
        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status, VerificationInvitation.STATUS_CONFIRMED
        )
        self.assertIsNotNone(self.invitation.completed_at)
        request = self.invitation.requests.get()
        self.assertEqual(request.request_type, UpdateRequest.REQUEST_CONFIRMATION)

    def test_modification_creates_request_without_touching_fiche(self):
        response = self.client.post(
            self.url,
            {"action": "modifier", "telephone": "06 98 76 54 32", "email": "nouveau@example.test"},
        )

        self.assertContains(response, "Merci")
        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status, VerificationInvitation.STATUS_PENDING_REVIEW
        )
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "")
        self.assertEqual(self.marie.email, "marie@example.test")
        request = self.invitation.requests.get()
        self.assertEqual(request.request_type, UpdateRequest.REQUEST_MODIFICATION)
        fields = list(request.fields.order_by("field_name"))
        self.assertEqual(len(fields), 2)
        self.assertEqual(fields[0].field_name, "email")
        self.assertEqual(fields[0].old_value, "marie@example.test")
        self.assertEqual(fields[0].new_value, "nouveau@example.test")

    def test_modification_without_change_is_rejected(self):
        response = self.client.post(
            self.url,
            {"action": "modifier", "telephone": "", "email": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucune modification proposée")
        self.assertEqual(self.invitation.requests.count(), 0)

    def test_stop_activity(self):
        response = self.client.post(self.url, {"action": "arreter"})
        self.assertContains(response, "Merci")
        request = self.invitation.requests.get()
        self.assertEqual(request.request_type, UpdateRequest.REQUEST_STOP_ACTIVITY)
        self.invitation.refresh_from_db()
        self.assertEqual(
            self.invitation.status, VerificationInvitation.STATUS_PENDING_REVIEW
        )

    def test_wrong_fiche(self):
        response = self.client.post(self.url, {"action": "fiche_incorrecte"})
        self.assertContains(response, "Merci")
        request = self.invitation.requests.get()
        self.assertEqual(request.request_type, UpdateRequest.REQUEST_WRONG_FICHE)

    def test_second_submission_is_blocked(self):
        self.client.post(self.url, {"action": "confirmer"})
        response = self.client.get(self.url)
        self.assertContains(response, "Merci")
        response = self.client.post(self.url, {"action": "confirmer"})
        self.assertEqual(response.status_code, 404)

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, {"action": "confirmer"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.invitation.requests.count(), 0)

    def test_rate_limited(self):
        for _ in range(20):
            self.client.post(self.url, {"action": "confirmer"})
        response = self.client.post(self.url, {"action": "confirmer"})
        self.assertEqual(response.status_code, 403)


class CampaignTestModeTests(TestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.avec_email = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.sans_email = _make_am("Martin", "Léa", telephone="06 12 34 56 78", commune=self.commune)
        self.campaign = _make_campaign(
            test_mode=True,
            test_emails="test1@exemple.fr, test2@exemple.fr",
        )

    def test_launch_sends_only_to_test_addresses(self):
        launch_campaign(self.campaign)

        self.assertEqual(len(mail.outbox), 2)
        for email in mail.outbox:
            self.assertEqual(email.to, ["test1@exemple.fr", "test2@exemple.fr"])
            self.assertNotIn("marie@example.test", email.to)
            self.assertTrue(email.subject.startswith("[TEST]"))
        self.assertEqual(
            self.campaign.invitations.filter(
                status=VerificationInvitation.STATUS_SENT
            ).count(),
            2,
        )

    def test_launch_requires_test_addresses(self):
        self.campaign.test_emails = ""
        self.campaign.save()
        with self.assertRaises(CampaignError):
            launch_campaign(self.campaign)
        self.assertEqual(len(mail.outbox), 0)

    def test_remind_sends_to_test_addresses(self):
        launch_campaign(self.campaign)
        mail.outbox.clear()
        remind_unanswered(self.campaign)

        self.assertEqual(len(mail.outbox), 2)
        for email in mail.outbox:
            self.assertEqual(email.to, ["test1@exemple.fr", "test2@exemple.fr"])

    def test_go_live_sends_real_and_invalidates_test_links(self):
        launch_campaign(self.campaign)
        test_link = None
        for email in mail.outbox:
            body = email.body
            if "/verification/" in body:
                test_link = body.split("/verification/")[1].split("/")[0]
        mail.outbox.clear()

        processed = go_live(self.campaign)

        self.assertEqual(processed, 2)
        self.campaign.refresh_from_db()
        self.assertFalse(self.campaign.test_mode)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["marie@example.test"])
        self.assertNotIn("[TEST]", mail.outbox[0].subject)
        invitation = self.campaign.invitations.get(structure=self.avec_email)
        self.assertEqual(invitation.status, VerificationInvitation.STATUS_SENT)
        letter = self.campaign.invitations.get(structure=self.sans_email)
        self.assertEqual(letter.status, VerificationInvitation.STATUS_NOT_CONTACTED)
        if test_link:
            response = self.client.get(
                reverse("campagnes:verification", kwargs={"token": test_link})
            )
            self.assertEqual(response.status_code, 404)

    def test_go_live_requires_test_mode(self):
        campaign = _make_campaign(name="Réelle", test_mode=False)
        launch_campaign(campaign)
        with self.assertRaises(CampaignError):
            go_live(campaign)

    def test_form_requires_test_emails_in_test_mode(self):
        form = UpdateCampaignForm(
            data={
                "name": "Campagne",
                "starts_at": date.today().isoformat(),
                "ends_at": (date.today() + timedelta(days=30)).isoformat(),
                "test_mode": "on",
                "test_emails": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("test_emails", form.errors)

    def test_form_rejects_invalid_test_email(self):
        form = UpdateCampaignForm(
            data={
                "name": "Campagne",
                "starts_at": date.today().isoformat(),
                "ends_at": (date.today() + timedelta(days=30)).isoformat(),
                "test_mode": "on",
                "test_emails": "pas-un-email",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("test_emails", form.errors)


class DashboardTestModeTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=PASSWORD,
        )
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.campaign = _make_campaign(
            test_mode=True,
            test_emails="test1@exemple.fr",
        )

    def test_detail_shows_test_badge(self):
        self.client.force_login(self.superuser)
        launch_campaign(self.campaign)
        response = self.client.get(
            reverse(
                "dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}
            )
        )
        self.assertContains(response, "Mode test")
        self.assertContains(response, "Passer en réel")

    def test_go_live_from_dashboard(self):
        self.client.force_login(self.superuser)
        launch_campaign(self.campaign)
        mail.outbox.clear()
        response = self.client.post(
            reverse("dashboard_campagnes:campaign_go_live", kwargs={"pk": self.campaign.pk})
        )
        self.assertRedirects(
            response,
            reverse("dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}),
        )
        self.campaign.refresh_from_db()
        self.assertFalse(self.campaign.test_mode)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["marie@example.test"])

    def test_go_live_requires_superuser(self):
        collaborateur = User.objects.create_user(
            username="col@example.test",
            email="col@example.test",
            password=PASSWORD,
            is_active=True,
        )
        self.client.force_login(collaborateur)
        response = self.client.post(
            reverse("dashboard_campagnes:campaign_go_live", kwargs={"pk": self.campaign.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_test_launch_from_dashboard(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:campaign_test_launch", kwargs={"pk": self.campaign.pk}
            ),
            {"test_emails": "test1@exemple.fr"},
        )
        self.assertRedirects(
            response,
            reverse("dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}),
        )
        self.campaign.refresh_from_db()
        self.assertTrue(self.campaign.test_mode)
        self.assertEqual(self.campaign.status, UpdateCampaign.STATUS_OPEN)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["test1@exemple.fr"])
        self.assertTrue(mail.outbox[0].subject.startswith("[TEST]"))

    def test_test_launch_requires_valid_addresses(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:campaign_test_launch", kwargs={"pk": self.campaign.pk}
            ),
            {"test_emails": "pas-un-email"},
        )
        self.assertRedirects(
            response,
            reverse("dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}),
        )
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, UpdateCampaign.STATUS_DRAFT)
        self.assertEqual(self.campaign.invitations.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_test_launch_requires_an_address(self):
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(
                "dashboard_campagnes:campaign_test_launch", kwargs={"pk": self.campaign.pk}
            ),
            {"test_emails": ""},
        )
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, UpdateCampaign.STATUS_DRAFT)
        self.assertEqual(len(mail.outbox), 0)

    def test_test_launch_requires_superuser(self):
        collaborateur = User.objects.create_user(
            username="col@example.test",
            email="col@example.test",
            password=PASSWORD,
            is_active=True,
        )
        self.client.force_login(collaborateur)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:campaign_test_launch", kwargs={"pk": self.campaign.pk}
            ),
            {"test_emails": "test1@exemple.fr"},
        )
        self.assertEqual(response.status_code, 302)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, UpdateCampaign.STATUS_DRAFT)

    def test_test_launch_only_from_brouillon(self):
        self.client.force_login(self.superuser)
        launch_campaign(self.campaign)
        self.campaign.refresh_from_db()
        self.assertEqual(self.campaign.status, UpdateCampaign.STATUS_OPEN)
        self.campaign.test_mode = False
        self.campaign.save(update_fields=["test_mode"])
        mail.outbox.clear()
        response = self.client.post(
            reverse(
                "dashboard_campagnes:campaign_test_launch", kwargs={"pk": self.campaign.pk}
            ),
            {"test_emails": "test1@exemple.fr"},
        )
        self.assertRedirects(
            response,
            reverse("dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}),
        )
        self.assertEqual(len(mail.outbox), 0)


class ReviewWorkflowTests(TestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.campaign = _make_campaign()
        self.invitation, _raw = VerificationInvitation.create_with_token(
            self.campaign, self.marie
        )
        self.request = submit_modification(
            self.invitation,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32", "email": "nouveau@example.test"},
        )
        self.superuser = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=PASSWORD,
        )

    def test_accept_all_applies_fields(self):
        review_request(self.request, "accept_all", [], "Vérifié par téléphone", self.superuser)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, UpdateRequest.STATUS_ACCEPTED)
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "06 98 76 54 32")
        self.assertEqual(self.marie.email, "nouveau@example.test")
        self.assertEqual(
            self.invitation.status, VerificationInvitation.STATUS_VALIDATED
        )
        self.assertEqual(
            self.request.fields.filter(
                decision=UpdateRequestField.DECISION_ACCEPTED
            ).count(),
            2,
        )

    def test_accept_selected_applies_only_checked_fields(self):
        phone_field = self.request.fields.get(field_name="telephone")
        review_request(
            self.request,
            "accept_selected",
            [phone_field.pk],
            "Seul le téléphone est accepté",
            self.superuser,
        )
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "06 98 76 54 32")
        self.assertEqual(self.marie.email, "marie@example.test")
        phone_field.refresh_from_db()
        self.assertEqual(phone_field.decision, UpdateRequestField.DECISION_ACCEPTED)
        email_field = self.request.fields.get(field_name="email")
        self.assertEqual(email_field.decision, UpdateRequestField.DECISION_REJECTED)

    def test_reject_applies_nothing(self):
        review_request(self.request, "reject", [], "Information à reconfirmer", self.superuser)
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "")

    def test_cannot_review_twice(self):
        review_request(self.request, "accept_all", [], "", self.superuser)
        with self.assertRaises(CampaignError):
            review_request(self.request, "accept_all", [], "", self.superuser)

    def test_review_is_audited(self):
        review_request(self.request, "reject", [], "Refusé", self.superuser)
        log = (
            AuditLog.objects.filter(model_name="UpdateRequest")
            .order_by("-pk")
            .first()
        )
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.superuser)
        self.assertEqual(log.object_id, self.request.pk)


class UpdateRequestFieldAuditTests(TestCase):
    def test_bulk_created_fields_are_audited(self):
        commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=commune)
        campaign = _make_campaign()
        invitation, _raw = VerificationInvitation.create_with_token(campaign, marie)
        inv = VerificationInvitation.objects.select_related("structure").get(
            pk=invitation.pk
        )

        request = submit_modification(
            inv,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32", "email": "nouveau@example.test"},
        )

        entry = AuditLog.objects.get(
            model_name="UpdateRequestField",
            action="create",
        )
        self.assertEqual(entry.object_id, request.pk)
        self.assertIn("2 champ(s)", entry.object_repr)
        self.assertEqual(len(entry.changes["fields"]), 2)


class AssistedRequestTests(TestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", commune=self.commune)
        self.campaign = _make_campaign()
        self.invitation, _raw = VerificationInvitation.create_with_token(
            self.campaign, self.marie
        )
        self.agent = User.objects.create_user(
            username="agent@example.test",
            email="agent@example.test",
            password=PASSWORD,
            is_active=True,
        )

    def test_agent_can_record_request_by_phone(self):
        request = create_assisted_request(
            self.invitation,
            UpdateRequest.REQUEST_MODIFICATION,
            {"telephone": "06 98 76 54 32"},
            VerificationInvitation.CHANNEL_PHONE,
            self.agent,
        )
        self.assertEqual(request.channel, VerificationInvitation.CHANNEL_PHONE)
        self.assertEqual(request.created_by, self.agent)
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "")


class DashboardCampaignTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=PASSWORD,
        )
        self.collaborateur = User.objects.create_user(
            username="col@example.test",
            email="col@example.test",
            password=PASSWORD,
            is_active=True,
        )
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.sans_email = _make_am(
            "Martin", "Léa", telephone="06 12 34 56 78", commune=self.commune
        )
        self.campaign = _make_campaign()
        UserCommune.objects.create(user=self.collaborateur, commune=self.commune)

    def test_campaign_list_requires_superuser(self):
        self.client.force_login(self.collaborateur)
        response = self.client.get(reverse("dashboard_campagnes:campaign_list"))
        self.assertRedirects(
            response,
            reverse("login") + "?next=" + reverse("dashboard_campagnes:campaign_list"),
        )

    def test_campaign_list_and_form_render(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("dashboard_campagnes:campaign_list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("dashboard_campagnes:campaign_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nouvelle campagne")

    def test_campaign_create_and_launch_via_dashboard(self):
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("dashboard_campagnes:campaign_add"),
            {
                "name": "Campagne test",
                "starts_at": date.today().isoformat(),
                "ends_at": (date.today() + timedelta(days=30)).isoformat(),
            },
        )
        self.assertRedirects(response, reverse("dashboard_campagnes:campaign_list"))
        campaign = UpdateCampaign.objects.get(name="Campagne test")
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_DRAFT)

        response = self.client.post(
            reverse("dashboard_campagnes:campaign_launch", kwargs={"pk": campaign.pk})
        )
        self.assertRedirects(
            response,
            reverse("dashboard_campagnes:campaign_detail", kwargs={"pk": campaign.pk}),
        )
        campaign.refresh_from_db()
        self.assertEqual(campaign.status, UpdateCampaign.STATUS_OPEN)

    def test_campaign_detail_shows_stats(self):
        self.client.force_login(self.superuser)
        launch_campaign(self.campaign)
        response = self.client.get(
            reverse(
                "dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fiches concernées")

    def test_collaborateur_cannot_access_campaign_management(self):
        self.client.force_login(self.collaborateur)
        response = self.client.get(
            reverse(
                "dashboard_campagnes:campaign_detail", kwargs={"pk": self.campaign.pk}
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_request_queue_scoped_by_commune(self):
        other_commune = Commune.objects.create(nom="Sains-du-Nord", code_postal="59177")
        other_am = _make_am("Zola", "Émile", commune=other_commune)
        other_campaign = _make_campaign(name="Autre campagne")
        other_invitation, _raw = VerificationInvitation.create_with_token(
            other_campaign, other_am
        )
        submit_modification(
            other_invitation,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 00 00 00 00"},
        )
        launch_campaign(self.campaign)
        self.invitation = self.campaign.invitations.get(structure=self.marie)
        submit_modification(
            self.invitation,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        self.client.force_login(self.collaborateur)
        response = self.client.get(reverse("dashboard_campagnes:request_queue"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dupont")
        self.assertNotContains(response, "Zola")

    def test_collaborateur_cannot_review_other_commune_request(self):
        other_commune = Commune.objects.create(nom="Sains-du-Nord", code_postal="59177")
        other_am = _make_am("Zola", "Émile", commune=other_commune)
        other_campaign = _make_campaign(name="Autre campagne")
        other_invitation, _raw = VerificationInvitation.create_with_token(
            other_campaign, other_am
        )
        other_request = submit_modification(
            other_invitation,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 00 00 00 00"},
        )
        self.client.force_login(self.collaborateur)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:request_review", kwargs={"pk": other_request.pk}
            ),
            {"decision": "reject"},
        )
        self.assertRedirects(response, reverse("dashboard_campagnes:request_queue"))
        other_request.refresh_from_db()
        self.assertEqual(other_request.status, UpdateRequest.STATUS_PENDING)

    def test_superuser_reviews_from_dashboard(self):
        launch_campaign(self.campaign)
        invitation = self.campaign.invitations.get(structure=self.marie)
        review = submit_modification(
            invitation,
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:request_review", kwargs={"pk": review.pk}
            ),
            {"decision": "accept_all", "comment": "ok"},
        )
        self.assertRedirects(response, reverse("dashboard_campagnes:request_queue"))
        self.marie.refresh_from_db()
        self.assertEqual(self.marie.telephone, "06 98 76 54 32")

    def test_assisted_request_from_dashboard(self):
        launch_campaign(self.campaign)
        invitation = self.campaign.invitations.get(structure=self.marie)
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse("dashboard_campagnes:assisted_request"),
            {
                "invitation": invitation.pk,
                "request_type": UpdateRequest.REQUEST_MODIFICATION,
                "channel": VerificationInvitation.CHANNEL_PHONE,
                "telephone": "06 98 76 54 32",
            },
        )
        self.assertRedirects(response, reverse("dashboard_campagnes:request_queue"))
        request = invitation.requests.get()
        self.assertEqual(request.request_type, UpdateRequest.REQUEST_MODIFICATION)
        self.assertEqual(request.channel, VerificationInvitation.CHANNEL_PHONE)
        self.assertEqual(request.created_by, self.superuser)

    def test_letters_page_prints_tokens(self):
        launch_campaign(self.campaign)
        self.client.force_login(self.superuser)
        response = self.client.post(
            reverse(
                "dashboard_campagnes:campaign_letters",
                kwargs={"pk": self.campaign.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre code personnel")
        self.assertContains(response, "/verification/")


class DashboardRequestQueueSectionsTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=PASSWORD,
        )
        self.commune = Commune.objects.create(nom="Fourmies", code_postal="59610")
        self.marie = _make_am("Dupont", "Marie", email="marie@example.test", commune=self.commune)
        self.lea = _make_am("Martin", "Léa", email="lea@example.test", commune=self.commune)
        self.campaign = _make_campaign()
        self.client.force_login(self.superuser)

    def _invitation(self, structure):
        return VerificationInvitation.create_with_token(self.campaign, structure)[0]

    def test_assisted_form_select_is_bounded_to_500_invitations(self):
        for index in range(510):
            structure = Structure.objects.create(
                nom=f"Structure {index}",
                commune=self.commune,
                type=TypeStructure.objects.get_or_create(nom="Assistante maternelle")[0],
            )
            VerificationInvitation.objects.create(
                campaign=self.campaign,
                structure=structure,
                token_hash=hashlib.sha256(f"token-{index}".encode()).hexdigest(),
            )

        response = self.client.get(reverse("dashboard_campagnes:request_queue"))

        self.assertEqual(response.status_code, 200)
        form = response.context["assisted_form"]
        self.assertEqual(form.fields["invitation"].queryset.count(), 500)
        self.assertContains(response, "Seules les 500 fiches les plus récentes")

    def test_confirmation_requests_are_shown_by_default(self):
        submit_confirmation(
            self._invitation(self.marie), VerificationInvitation.CHANNEL_EMAIL
        )
        response = self.client.get(reverse("dashboard_campagnes:request_queue"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirmé sans modification")
        self.assertContains(response, "Confirmation sans modification (1)")

    def test_filter_by_category(self):
        submit_confirmation(
            self._invitation(self.marie), VerificationInvitation.CHANNEL_EMAIL
        )
        submit_modification(
            self._invitation(self.lea),
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"),
            {"categorie": UpdateRequest.REQUEST_CONFIRMATION},
        )
        self.assertContains(response, "Confirmation sans modification (1)")
        self.assertContains(response, "Proposition de modification (0)")
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"),
            {"categorie": UpdateRequest.REQUEST_MODIFICATION},
        )
        self.assertContains(response, "Proposition de modification (1)")
        self.assertContains(response, "Confirmation sans modification (0)")

    def test_filter_by_status(self):
        request = submit_modification(
            self._invitation(self.marie),
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        review_request(request, "accept_all", [], "", self.superuser)
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"),
            {"statut": UpdateRequest.STATUS_ACCEPTED},
        )
        self.assertContains(response, "Acceptée")
        self.assertContains(response, "Proposition de modification (1)")
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"),
            {"statut": "en_attente"},
        )
        self.assertContains(response, "Proposition de modification (0)")

    def test_filter_by_campaign(self):
        other_campaign = _make_campaign(name="Autre campagne")
        other_invitation = VerificationInvitation.create_with_token(
            other_campaign, self.lea
        )[0]
        submit_confirmation(other_invitation, VerificationInvitation.CHANNEL_EMAIL)
        submit_modification(
            self._invitation(self.marie),
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"),
            {"campagne": str(other_campaign.pk)},
        )
        self.assertContains(response, "Confirmation sans modification (1)")
        self.assertContains(response, "Proposition de modification (0)")

    def test_search_by_name(self):
        submit_confirmation(
            self._invitation(self.marie), VerificationInvitation.CHANNEL_EMAIL
        )
        submit_modification(
            self._invitation(self.lea),
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        response = self.client.get(
            reverse("dashboard_campagnes:request_queue"), {"q": "Martin"}
        )
        self.assertContains(response, "Proposition de modification (1)")
        self.assertContains(response, "Confirmation sans modification (0)")

    def test_table_shows_before_after_comparison(self):
        submit_modification(
            self._invitation(self.marie),
            VerificationInvitation.CHANNEL_EMAIL,
            {"telephone": "06 98 76 54 32"},
        )
        response = self.client.get(reverse("dashboard_campagnes:request_queue"))
        self.assertContains(response, "Téléphone")
        self.assertContains(response, "→")
        self.assertContains(response, "06 98 76 54 32")