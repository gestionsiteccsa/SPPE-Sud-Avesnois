from django.contrib.auth import authenticate, get_user_model
from django.core.cache import caches
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from authentication.forms import DashboardUserCreateForm, DashboardUserUpdateForm
from authentication.models import (
    CollaborateurInscription,
    DestinataireNotification,
    UserCommune,
)
from communes.models import Commune
from structures.models import AuditLog


User = get_user_model()


class DashboardUserFormTests(TestCase):
    def test_create_requires_email(self):
        password = "Un-mot-de-passe-tres-long-2026"
        form = DashboardUserCreateForm(
            data={
                "email": "",
                "password1": password,
                "password2": password,
                "is_superuser": True,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_create_rejects_weak_password(self):
        form = DashboardUserCreateForm(
            data={
                "email": "nouveau@example.test",
                "password1": "password",
                "password2": "password",
                "is_superuser": True,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_create_requires_password_confirmation(self):
        form = DashboardUserCreateForm(
            data={
                "email": "nouveau@example.test",
                "password1": "Un-mot-de-passe-tres-long-2026",
                "password2": "",
                "is_superuser": True,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_email_is_unique_ignoring_case(self):
        User.objects.create_user(
            username="existant@example.test",
            email="existant@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        form = DashboardUserCreateForm(
            data={
                "email": "EXISTANT@example.test",
                "password1": "Un-autre-mot-de-passe-tres-long-2026",
                "password2": "Un-autre-mot-de-passe-tres-long-2026",
                "is_superuser": False,
                "is_active": True,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_valid_form_hashes_password_and_aligns_staff_status(self):
        password = "Un-mot-de-passe-tres-long-2026"
        form = DashboardUserCreateForm(
            data={
                "email": "nouveau@example.test",
                "password1": password,
                "password2": password,
                "is_superuser": True,
                "is_active": True,
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)

    def test_last_active_superuser_cannot_be_demoted(self):
        user = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        form = DashboardUserUpdateForm(
            instance=user,
            data={
                "email": user.email,
                "is_superuser": False,
                "is_active": True,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class EmailBackendTests(TestCase):
    def test_duplicate_email_fails_closed(self):
        password = "Un-mot-de-passe-tres-long-2026"
        User.objects.create_user(
            username="premier",
            email="doublon@example.test",
            password=password,
        )
        User.objects.create_user(
            username="second",
            email="doublon@example.test",
            password=password,
        )

        self.assertIsNone(authenticate(username="doublon@example.test", password=password))


class PasswordResetRateLimitTests(TestCase):
    def setUp(self):
        caches["ratelimit"].clear()

    def test_password_reset_is_rate_limited(self):
        url = reverse("password_reset")

        for _attempt in range(10):
            response = self.client.post(url, {"email": "inconnu@example.test"})
            self.assertEqual(response.status_code, 302)

        response = self.client.post(url, {"email": "inconnu@example.test"})

        self.assertEqual(response.status_code, 403)


class LoginRateLimitTests(TestCase):
    def setUp(self):
        caches["ratelimit"].clear()

    def test_login_is_rate_limited_per_account(self):
        url = reverse("login")

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
        url = reverse("login")

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


class DashboardUserDeleteTests(TestCase):
    def test_last_active_superuser_cannot_be_deleted(self):
        admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(admin)

        response = self.client.post(reverse("dashboard:user_delete", args=[admin.pk]))

        self.assertRedirects(response, reverse("dashboard:user_list"))
        self.assertTrue(User.objects.filter(pk=admin.pk).exists())


class CollaborateurInscriptionTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        caches["ratelimit"].clear()
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )

    def _register(self, email="collab@example.test"):
        return self.client.post(
            reverse("inscription"),
            {
                "prenom": "Camille",
                "nom": "Durand",
                "email": email,
                "password1": self.password,
                "password2": self.password,
            },
        )

    def test_registration_creates_inactive_user_pending_request_and_notifies_admin(self):
        response = self._register()

        self.assertRedirects(response, reverse("inscription_done"))
        user = User.objects.get(email="collab@example.test")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.first_name, "Camille")
        self.assertEqual(user.last_name, "Durand")
        inscription = CollaborateurInscription.objects.get(user=user)
        self.assertEqual(inscription.statut, CollaborateurInscription.STATUT_EN_ATTENTE)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.admin.email])
        self.assertIn("Nouvelle demande d'inscription", mail.outbox[0].subject)

    def test_pending_user_cannot_login(self):
        self._register()
        user = User.objects.get(email="collab@example.test")

        self.assertIsNone(authenticate(username=user.email, password=self.password))

    def test_duplicate_email_is_rejected(self):
        self._register()

        response = self._register()

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFormError(form, "email", "Un compte utilise déjà cette adresse email.")
        self.assertEqual(User.objects.filter(email__iexact="collab@example.test").count(), 1)

    def test_validation_activates_user_and_notifies_collaborator(self):
        self._register()
        inscription = CollaborateurInscription.objects.get()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "valider"},
        )

        self.assertRedirects(response, reverse("dashboard:inscription_list"))
        inscription.refresh_from_db()
        user = User.objects.get(pk=inscription.user_id)
        self.assertTrue(user.is_active)
        self.assertEqual(inscription.statut, CollaborateurInscription.STATUT_VALIDEE)
        self.assertEqual(inscription.decideur, self.admin)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, [user.email])
        self.assertIn("validée", mail.outbox[1].subject)

    def test_refusal_keeps_user_inactive_and_notifies(self):
        self._register()
        inscription = CollaborateurInscription.objects.get()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "refuser"},
        )

        self.assertRedirects(response, reverse("dashboard:inscription_list"))
        inscription.refresh_from_db()
        self.assertEqual(inscription.statut, CollaborateurInscription.STATUT_REFUSEE)
        user = User.objects.get(pk=inscription.user_id)
        self.assertFalse(user.is_active)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].to, [user.email])

    def test_decide_requires_superuser(self):
        self._register()
        inscription = CollaborateurInscription.objects.get()
        collaborator = User.objects.create_user(
            username="normal@example.test",
            email="normal@example.test",
            password=self.password,
        )
        self.client.force_login(collaborator)

        response = self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "valider"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)
        inscription.refresh_from_db()
        self.assertEqual(inscription.statut, CollaborateurInscription.STATUT_EN_ATTENTE)

    def test_already_decided_request_cannot_be_decided_again(self):
        self._register()
        inscription = CollaborateurInscription.objects.get()
        self.client.force_login(self.admin)
        self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "valider"},
        )

        response = self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "refuser"},
        )

        self.assertRedirects(response, reverse("dashboard:inscription_list"))
        inscription.refresh_from_db()
        self.assertEqual(inscription.statut, CollaborateurInscription.STATUT_VALIDEE)

    def test_inscription_list_shows_pending_count_for_superuser(self):
        self._register()
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard:inscription_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["pending_inscriptions_count"], 1)

    def test_collaborator_login_redirects_to_structures(self):
        user = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )
        UserCommune.objects.create(
            user=user,
            commune=Commune.objects.create(nom="Marseille", code_postal="13001"),
        )

        response = self.client.post(
            reverse("login"),
            {"username": user.email, "password": self.password},
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))


class DashboardUserUpdateCommunesTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def test_communes_are_saved_and_replaced(self):
        collaborator = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )
        commune_a = Commune.objects.create(nom="Marseille", code_postal="13001")
        commune_b = Commune.objects.create(nom="Aix-en-Provence", code_postal="13100")
        UserCommune.objects.create(user=collaborator, commune=commune_a)

        form = DashboardUserUpdateForm(
            data={
                "email": "collab@example.test",
                "is_superuser": False,
                "is_active": True,
                "communes": [commune_b.pk],
            },
            instance=collaborator,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(
            list(UserCommune.objects.filter(user=collaborator).values_list("commune_id", flat=True)),
            [commune_b.pk],
        )


class NotificationConfigTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )

    def test_page_requires_superuser(self):
        collaborator = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )
        self.client.force_login(collaborator)

        response = self.client.get(reverse("dashboard:notification_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_page_lists_every_recipient_and_summarizes_delivery(self):
        recipients = [
            DestinataireNotification(
                email=f"destinataire-{index:02d}@example.test",
                actif=index < 3,
                en_cci=index == 2,
            )
            for index in range(26)
        ]
        DestinataireNotification.objects.bulk_create(recipients)
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard:notification_list"))

        self.assertEqual(len(response.context["destinataires"]), 26)
        self.assertEqual(
            response.context["notification_summary"],
            {
                "total": 26,
                "active": 3,
                "primary": 2,
                "blind_copy": 1,
                "fallback_active": False,
            },
        )
        self.assertContains(response, "destinataire-25@example.test")

    def test_add_recipient(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "accueil@example.test", "actif": "on"},
        )

        self.assertRedirects(response, reverse("dashboard:notification_list"))
        dest = DestinataireNotification.objects.get(email="accueil@example.test")
        self.assertTrue(dest.actif)
        self.assertFalse(dest.en_cci)

    def test_add_recipient_in_cci(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "copie@example.test", "actif": "on", "en_cci": "on"},
        )

        self.assertRedirects(response, reverse("dashboard:notification_list"))
        dest = DestinataireNotification.objects.get(email="copie@example.test")
        self.assertTrue(dest.actif)
        self.assertTrue(dest.en_cci)

    def test_duplicate_email_is_rejected(self):
        DestinataireNotification.objects.create(email="doublon@example.test")
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "doublon@example.test"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DestinataireNotification.objects.count(), 1)

    def test_invalid_email_is_rejected(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "pas-un-email"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(DestinataireNotification.objects.count(), 0)

    def test_invalid_addition_keeps_selected_options(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "pas-un-email", "en_cci": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"]["actif"].value())
        self.assertTrue(response.context["form"]["en_cci"].value())

    def test_delete_page_asks_for_confirmation(self):
        dest = DestinataireNotification.objects.create(
            email="a-confirmer@example.test"
        )
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse("dashboard:notification_delete", args=[dest.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, dest.email)
        self.assertTrue(DestinataireNotification.objects.filter(pk=dest.pk).exists())

    def test_selection_and_cci_are_updated(self):
        principale = DestinataireNotification.objects.create(email="principale@example.test")
        copie = DestinataireNotification.objects.create(email="copie@example.test")
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_update"),
            {"actif": [str(copie.pk)], "en_cci": [str(principale.pk)]},
        )

        self.assertRedirects(response, reverse("dashboard:notification_list"))
        principale.refresh_from_db()
        copie.refresh_from_db()
        self.assertFalse(principale.actif)
        self.assertTrue(principale.en_cci)
        self.assertTrue(copie.actif)
        self.assertFalse(copie.en_cci)

    def test_recipient_can_be_deleted(self):
        dest = DestinataireNotification.objects.create(email="a-supprimer@example.test")
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:notification_delete", args=[dest.pk])
        )

        self.assertRedirects(response, reverse("dashboard:notification_list"))
        self.assertFalse(DestinataireNotification.objects.filter(pk=dest.pk).exists())


class NotificationEmailTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        caches["ratelimit"].clear()
        User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )

    def _register(self):
        return self.client.post(
            reverse("inscription"),
            {
                "prenom": "Camille",
                "nom": "Durand",
                "email": "collab@example.test",
                "password1": self.password,
                "password2": self.password,
            },
        )

    def test_registration_notifies_configured_recipients_with_cc(self):
        DestinataireNotification.objects.create(email="principale@example.test")
        DestinataireNotification.objects.create(email="copie@example.test", en_cci=True)
        DestinataireNotification.objects.create(email="inactive@example.test", actif=False)

        self._register()

        email = mail.outbox[0]
        self.assertEqual(email.to, ["principale@example.test"])
        self.assertEqual(email.cc, ["copie@example.test"])
        self.assertNotIn("inactive@example.test", email.to + email.cc)
        self.assertNotIn("admin@example.test", email.to + email.cc)

    def test_registration_falls_back_to_superusers_without_active_recipient(self):
        DestinataireNotification.objects.create(email="inactive@example.test", actif=False)

        self._register()

        email = mail.outbox[0]
        self.assertEqual(email.to, ["admin@example.test"])
        self.assertEqual(email.cc, [])


class PasswordResetEmailTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        caches["ratelimit"].clear()
        self.user = User.objects.create_user(
            username="utilisateur@example.test",
            email="utilisateur@example.test",
            password=self.password,
            first_name="Louise",
            last_name="Martin",
        )

    def test_reset_email_is_sent_to_requesting_user(self):
        response = self.client.post(
            reverse("password_reset"), {"email": self.user.email}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [self.user.email])
        self.assertIn("Réinitialisation de votre mot de passe", email.subject)
        self.assertIn("/mot-de-passe-oublie/", email.body)

    def test_no_email_is_sent_for_unknown_address(self):
        response = self.client.post(
            reverse("password_reset"), {"email": "inconnu@example.test"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_is_sent_for_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            reverse("password_reset"), {"email": self.user.email}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


class DashboardProfileTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        self.user = User.objects.create_user(
            username="prof@example.test",
            email="prof@example.test",
            password=self.password,
            first_name="Camille",
            last_name="Durand",
        )

    def _profile_data(self, **overrides):
        data = {
            "first_name": "Camille",
            "last_name": "Durand",
            "email": "prof@example.test",
            "current_password": self.password,
        }
        data.update(overrides)
        return data

    def test_profile_requires_login(self):
        response = self.client.get(reverse("dashboard:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_profile_updates_name_and_email_and_syncs_username(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("dashboard:profile"),
            self._profile_data(
                first_name="Louise",
                last_name="Martin",
                email="nouveau@example.test",
            ),
        )

        self.assertRedirects(response, reverse("dashboard:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Louise")
        self.assertEqual(self.user.last_name, "Martin")
        self.assertEqual(self.user.email, "nouveau@example.test")
        self.assertEqual(self.user.username, "nouveau@example.test")

    def test_profile_rejects_duplicate_email(self):
        User.objects.create_user(
            username="autre@example.test",
            email="autre@example.test",
            password=self.password,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("dashboard:profile"),
            self._profile_data(email="AUTRE@example.test"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Un compte utilise déjà cette adresse email.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "prof@example.test")

    def test_profile_requires_current_password(self):
        self.client.force_login(self.user)

        data = self._profile_data(email="nouveau@example.test")
        data["current_password"] = ""
        response = self.client.post(reverse("dashboard:profile"), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("current_password", response.context["form"].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "prof@example.test")

    def test_profile_rejects_wrong_password(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("dashboard:profile"),
            self._profile_data(
                email="nouveau@example.test",
                current_password="mot-de-passe-incorrect",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Le mot de passe actuel est incorrect.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "prof@example.test")

    def test_profile_logs_changes_in_audit(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse("dashboard:profile"),
            self._profile_data(first_name="Louise", email="nouveau@example.test"),
        )

        log = AuditLog.objects.get(user=self.user, action="update", model_name="User")
        self.assertEqual(log.changes["first_name"], {"old": "Camille", "new": "Louise"})
        self.assertEqual(
            log.changes["email"],
            {"old": "prof@example.test", "new": "nouveau@example.test"},
        )
        self.assertNotIn("last_name", log.changes)

    def test_profile_does_not_log_unchanged_profile(self):
        self.client.force_login(self.user)

        self.client.post(reverse("dashboard:profile"), self._profile_data())

        self.assertFalse(
            AuditLog.objects.filter(
                user=self.user, action="update", model_name="User"
            ).exists()
        )
