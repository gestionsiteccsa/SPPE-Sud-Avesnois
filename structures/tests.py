import json
import os
import re
import sqlite3
import shutil
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from authentication.models import (
    CollaborateurInscription,
    DestinataireNotification,
    UserCommune,
)
from communes.models import Commune
from structures.audit import audit_actor
from structures.models import AuditLog, Structure, TypeStructure
from structures.services.import_data import ImportDataError, import_rows
from structures.services.sqlite_backup import (
    SQLiteBackupError,
    backup_lock,
    create_sqlite_backup,
    delete_sqlite_backup,
    list_sqlite_backups,
    mark_backup_verified,
    purge_sqlite_backups,
    run_backup,
    verify_sqlite_database,
)
from structures.services.stats import build_dashboard_statistics


User = get_user_model()


class DashboardStatisticsServiceTests(TestCase):
    def setUp(self):
        self.commune = Commune.objects.create(nom="Testville", code_postal="75001")
        self.type = TypeStructure.objects.create(nom="Accueil de loisirs")

    def test_offer_excludes_hidden_structures_but_quality_includes_them(self):
        Structure.objects.create(
            nom="Structure visible renseignée",
            afficher=True,
            commune=self.commune,
            type=self.type,
            nb_places_total=20,
            places_disponibles=4,
            telephone="0102030405",
            latitude=50.0,
            longitude=4.0,
        )
        Structure.objects.create(
            nom="Structure visible sans capacité",
            afficher=True,
            commune=self.commune,
            type=self.type,
            places_non_communique=True,
        )
        Structure.objects.create(
            nom="Structure masquée",
            afficher=False,
            commune=self.commune,
            type=self.type,
            nb_places_total=100,
            email="contact@example.test",
        )

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(
            statistics["offer"],
            {
                "structures": 2,
                "capacity_total": 20,
                "capacity_average": 20.0,
                "capacity_known": 1,
                "capacity_missing": 1,
                "available_places": 4,
                "availability_known": 1,
            },
        )
        capacity_quality = statistics["completeness"][0]
        self.assertEqual(capacity_quality["total"], 2)
        self.assertEqual(capacity_quality["missing"], 1)
        self.assertEqual(capacity_quality["percent"], 67)
        self.assertEqual(
            statistics["by_type"]["counts"],
            [{"label": self.type.nom, "total": 2}],
        )

    def test_grouped_statistics_keep_totals_in_an_others_bucket(self):
        types = [
            TypeStructure.objects.create(nom=f"Type {index}") for index in range(4)
        ]
        capacities = (10, 20, 30, 100)
        quantities = (4, 3, 2, 1)
        structures = []
        for type_, capacity, quantity in zip(types, capacities, quantities):
            structures.extend(
                Structure(
                    nom=f"{type_.nom} — {index}",
                    afficher=True,
                    commune=self.commune,
                    type=type_,
                    nb_places_total=capacity,
                )
                for index in range(quantity)
            )
        Structure.objects.bulk_create(structures)

        statistics = build_dashboard_statistics(
            reference_date=date(2026, 8, 18),
            group_limit=3,
        )

        type_counts = statistics["by_type"]["counts"]
        type_capacities = statistics["by_type"]["capacities"]
        self.assertEqual(type_counts[-1], {"label": "Autres", "total": 3})
        self.assertEqual(sum(item["total"] for item in type_counts), 10)
        self.assertEqual(type_capacities[-1]["label"], "Autres")
        self.assertEqual(sum(item["total"] for item in type_capacities), 260)

    def test_capacity_average_is_unknown_when_no_capacity_is_provided(self):
        Structure.objects.create(
            nom="Structure sans capacité",
            afficher=True,
            commune=self.commune,
            type=self.type,
        )

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(statistics["offer"]["capacity_total"], 0)
        self.assertIsNone(statistics["offer"]["capacity_average"])
        self.assertEqual(statistics["offer"]["capacity_known"], 0)
        self.assertEqual(statistics["offer"]["capacity_missing"], 1)

    def test_completeness_covers_age_contact_and_geolocation(self):
        Structure.objects.create(
            nom="Fiche renseignée",
            afficher=False,
            nb_places_total=12,
            age_non_renseigne=False,
            age_min=3,
            telephone="0102030405",
            latitude=50.0,
            longitude=4.0,
        )
        Structure.objects.create(nom="Fiche à compléter", afficher=True)

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(
            [item["total"] for item in statistics["completeness"]],
            [1, 1, 1, 1],
        )
        self.assertEqual(
            [item["percent"] for item in statistics["completeness"]],
            [50, 50, 50, 50],
        )

    def test_freshness_uses_source_date_buckets(self):
        source_dates = (
            date(2026, 7, 1),
            date(2026, 4, 1),
            date(2025, 10, 1),
            date(2025, 1, 1),
            None,
        )
        Structure.objects.bulk_create(
            [
                Structure(
                    nom=f"Structure {index}",
                    date_mise_a_jour_monenfant=source_date,
                )
                for index, source_date in enumerate(source_dates)
            ]
        )

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(
            [item["total"] for item in statistics["freshness"]],
            [1, 1, 1, 1, 1],
        )
        self.assertEqual(statistics["freshness_outdated"], 2)

    def test_freshness_assigns_exact_boundaries_to_the_older_bucket(self):
        Structure.objects.bulk_create(
            [
                Structure(
                    nom="Exactement trois mois",
                    date_mise_a_jour_monenfant=date(2026, 5, 18),
                ),
                Structure(
                    nom="Exactement six mois",
                    date_mise_a_jour_monenfant=date(2026, 2, 18),
                ),
                Structure(
                    nom="Exactement douze mois",
                    date_mise_a_jour_monenfant=date(2025, 8, 18),
                ),
            ]
        )

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(
            [item["total"] for item in statistics["freshness"]],
            [0, 1, 2, 0, 0],
        )
        self.assertEqual(statistics["freshness_outdated"], 2)

    def test_opening_days_count_each_structure_once(self):
        Structure.objects.create(
            nom="Ouverte lundi",
            afficher=True,
            horaires=[
                {"jour": "lundi", "ferme": False},
                {"jour": "lundi", "ferme": False},
                {"jour": "mardi", "ferme": True},
            ],
        )
        Structure.objects.create(nom="Horaires absents", afficher=True, horaires=[])
        Structure.objects.create(
            nom="Structure masquée ouverte",
            afficher=False,
            horaires=[{"jour": "lundi", "ferme": False}],
        )

        statistics = build_dashboard_statistics(reference_date=date(2026, 8, 18))

        self.assertEqual(statistics["opening_days"][0]["total"], 1)
        self.assertEqual(statistics["opening_days"][1]["total"], 0)

    def test_statistics_query_count_does_not_depend_on_structure_count(self):
        Structure.objects.bulk_create(
            [
                Structure(
                    nom=f"Structure {index}",
                    afficher=True,
                    commune=self.commune,
                    type=self.type,
                )
                for index in range(12)
            ]
        )

        with self.assertNumQueries(6):
            build_dashboard_statistics(reference_date=date(2026, 8, 18))


class StructureImportTests(TestCase):
    def test_replace_import_rolls_back_when_one_row_is_invalid(self):
        Structure.objects.create(nom="Structure existante")
        rows = [
            {"NOM": "Structure valide"},
            {"NOM": "Structure invalide", "email": "adresse-invalide"},
        ]

        with self.assertRaises(ImportDataError):
            import_rows(rows, replace=True, actor=None)

        self.assertQuerySetEqual(
            Structure.objects.values_list("nom", flat=True),
            ["Structure existante"],
        )

    def test_import_stores_source_date_in_monenfant_field(self):
        import_rows(
            [{"NOM": "Structure exemple", "Date mise à jour": "03/02/2026"}],
            replace=False,
            actor=None,
        )

        structure = Structure.objects.get()
        self.assertEqual(structure.date_mise_a_jour_monenfant.isoformat(), "2026-02-03")


class StructureConstraintTests(TestCase):
    def test_database_rejects_negative_available_places(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Structure.objects.create(nom="Structure invalide", places_disponibles=-1)

    def test_model_rejects_inverted_age_range(self):
        structure = Structure(
            nom="Structure invalide",
            age_min=3,
            age_min_unite="ans",
            age_max=12,
            age_max_unite="mois",
        )

        with self.assertRaises(ValidationError):
            structure.full_clean()


class StructureAuditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="audit@example.test",
            email="audit@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.structure = Structure.objects.create(nom="Ancien nom")
        AuditLog.objects.all().delete()

    def test_update_records_actor_and_changed_values(self):
        self.structure.nom = "Nouveau nom"

        with audit_actor(self.user):
            self.structure.save()

        entry = AuditLog.objects.get(action="update")
        self.assertEqual(entry.user, self.user)
        self.assertEqual(
            entry.changes["nom"],
            {"old": "Ancien nom", "new": "Nouveau nom"},
        )

    def test_delete_records_actor(self):
        structure_id = self.structure.pk

        with audit_actor(self.user):
            self.structure.delete()

        entry = AuditLog.objects.get(action="delete", object_id=structure_id)
        self.assertEqual(entry.user, self.user)


class StructureAuditQueryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="audit@example.test",
            email="audit@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.structure = Structure.objects.create(nom="Ancien nom")

    def test_update_loaded_via_orm_avoids_extra_select(self):
        AuditLog.objects.all().delete()
        loaded = Structure.objects.get(pk=self.structure.pk)
        loaded.nom = "Nouveau nom"

        with self.assertNumQueries(2):
            with audit_actor(self.user):
                loaded.save()

        entry = AuditLog.objects.get(action="update")
        self.assertEqual(entry.user, self.user)
        self.assertEqual(
            entry.changes["nom"],
            {"old": "Ancien nom", "new": "Nouveau nom"},
        )


class PurgeAuditLogTests(TestCase):
    def test_purges_only_entries_older_than_retention(self):
        old = AuditLog.objects.create(
            user=None,
            action="update",
            model_name="Structure",
        )
        AuditLog.objects.filter(pk=old.pk).update(
            timestamp=timezone.now() - timedelta(days=400)
        )
        recent = AuditLog.objects.create(
            user=None,
            action="update",
            model_name="Structure",
        )

        call_command("purge_audit_log", "--older-than-days", "365")

        self.assertFalse(AuditLog.objects.filter(pk=old.pk).exists())
        self.assertTrue(AuditLog.objects.filter(pk=recent.pk).exists())


class AuditCoverageTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )
        self.client.force_login(self.admin)

    def _entries(self, model_name, action):
        return AuditLog.objects.filter(
            user=self.admin, model_name=model_name, action=action
        )

    def test_commune_crud_is_logged_with_actor_and_values(self):
        response = self.client.post(
            reverse("dashboard:commune_add"),
            {"nom": "Lille", "code_postal": "59000"},
        )
        self.assertRedirects(response, reverse("dashboard:commune_list"))
        commune = Commune.objects.get(nom="Lille")
        entry = self._entries("Commune", "create").get(object_id=commune.pk)
        self.assertEqual(entry.changes, {"_created": True})
        self.assertEqual(entry.user, self.admin)

        self.client.post(
            reverse("dashboard:commune_edit", args=[commune.pk]),
            {"nom": "Lille Centre", "code_postal": "59000"},
        )
        entry = self._entries("Commune", "update").get(object_id=commune.pk)
        self.assertEqual(
            entry.changes["nom"], {"old": "Lille", "new": "Lille Centre"}
        )

        self.client.post(reverse("dashboard:commune_delete", args=[commune.pk]))
        self.assertTrue(
            self._entries("Commune", "delete").filter(object_id=commune.pk).exists()
        )

    def test_type_crud_is_logged_with_actor_and_values(self):
        self.client.post(reverse("dashboard:type_add"), {"nom": "Crèche familiale"})
        type_ = TypeStructure.objects.get(nom="Crèche familiale")
        self.assertTrue(
            self._entries("TypeStructure", "create").filter(object_id=type_.pk).exists()
        )

        self.client.post(
            reverse("dashboard:type_edit", args=[type_.pk]),
            {"nom": "Crèche familiale 2"},
        )
        entry = self._entries("TypeStructure", "update").get(object_id=type_.pk)
        self.assertEqual(
            entry.changes["nom"],
            {"old": "Crèche familiale", "new": "Crèche familiale 2"},
        )

        self.client.post(reverse("dashboard:type_delete", args=[type_.pk]))
        self.assertTrue(
            self._entries("TypeStructure", "delete").filter(object_id=type_.pk).exists()
        )

    def test_user_crud_is_logged(self):
        self.client.post(
            reverse("dashboard:user_add"),
            {
                "email": "nouveau@example.test",
                "password1": self.password,
                "password2": self.password,
                "is_active": "on",
            },
        )
        user = User.objects.get(email="nouveau@example.test")
        entry = self._entries("User", "create").get(object_id=user.pk)
        self.assertEqual(entry.changes["email"]["new"], "nouveau@example.test")
        self.assertEqual(entry.user, self.admin)

        self.client.post(
            reverse("dashboard:user_edit", args=[user.pk]),
            {"email": "nouveau@example.test"},
        )
        entry = self._entries("User", "update").get(object_id=user.pk)
        self.assertEqual(entry.changes["is_active"], {"old": True, "new": False})

        self.client.post(reverse("dashboard:user_delete", args=[user.pk]))
        self.assertTrue(
            self._entries("User", "delete")
            .filter(object_repr="nouveau@example.test")
            .exists()
        )

    def test_inscription_decision_is_logged_with_decider(self):
        user = User.objects.create_user(
            username="pendant@example.test",
            email="pendant@example.test",
            password=self.password,
            is_active=False,
        )
        inscription = CollaborateurInscription.objects.create(user=user)

        self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "valider"},
        )

        entry = self._entries("Inscription", "update").get(object_id=inscription.pk)
        self.assertEqual(entry.user, self.admin)
        self.assertEqual(entry.changes["statut"]["new"], "validee")
        self.assertEqual(entry.changes["is_active"]["new"], True)

    def test_inscription_refusal_is_logged(self):
        user = User.objects.create_user(
            username="pendant2@example.test",
            email="pendant2@example.test",
            password=self.password,
            is_active=False,
        )
        inscription = CollaborateurInscription.objects.create(user=user)

        self.client.post(
            reverse("dashboard:inscription_decide", args=[inscription.pk]),
            {"action": "refuser"},
        )

        entry = self._entries("Inscription", "update").get(object_id=inscription.pk)
        self.assertEqual(entry.changes["statut"]["new"], "refusee")

    def test_notification_config_is_logged(self):
        self.client.post(
            reverse("dashboard:notification_add"),
            {"email": "accueil@example.test", "actif": "on"},
        )
        dest = DestinataireNotification.objects.get(email="accueil@example.test")
        self.assertTrue(
            self._entries("Notification", "create").filter(object_id=dest.pk).exists()
        )

        self.client.post(reverse("dashboard:notification_update"), {"en_cci": [str(dest.pk)]})
        entry = self._entries("Notification", "update").get(object_id=dest.pk)
        self.assertEqual(entry.changes["actif"], {"old": True, "new": False})
        self.assertEqual(entry.changes["en_cci"], {"old": False, "new": True})

        self.client.post(reverse("dashboard:notification_delete", args=[dest.pk]))
        self.assertTrue(
            self._entries("Notification", "delete").filter(object_id=dest.pk).exists()
        )

    def test_password_change_is_logged_without_secret(self):
        response = self.client.post(
            reverse("dashboard:password_change"),
            {
                "old_password": self.password,
                "new_password1": "Nouveau-mot-de-passe-2026!",
                "new_password2": "Nouveau-mot-de-passe-2026!",
            },
        )
        self.assertEqual(response.status_code, 302)

        entry = self._entries("User", "update").get(
            object_id=self.admin.pk
        )
        self.assertEqual(entry.changes, {"_password_changed": True})

    def test_journal_requires_superuser(self):
        collaborator = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )
        self.client.force_login(collaborator)

        response = self.client.get(reverse("dashboard:audit_log"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_journal_filters_by_model_action_and_user(self):
        self.client.post(
            reverse("dashboard:commune_add"),
            {"nom": "Ville Test Journal", "code_postal": "59001"},
        )
        self.client.post(
            reverse("dashboard:type_add"), {"nom": "Type Test Journal"}
        )
        self.client.get(reverse("dashboard:audit_log"))

        by_model = self.client.get(reverse("dashboard:audit_log"), {"model": "Commune"})
        self.assertContains(by_model, "Ville Test Journal")
        self.assertNotContains(by_model, "Type Test Journal")

        by_action = self.client.get(reverse("dashboard:audit_log"), {"action": "create"})
        self.assertContains(by_action, "Ville Test Journal")
        self.assertContains(by_action, "Type Test Journal")

        by_user = self.client.get(
            reverse("dashboard:audit_log"), {"user": str(self.admin.pk)}
        )
        self.assertContains(by_user, "Ville Test Journal")


class DashboardImportTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )

    def test_import_requires_superuser(self):
        response = self.client.get(reverse("dashboard:import_data"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_failed_replace_upload_keeps_existing_rows(self):
        self.client.force_login(self.admin)
        Structure.objects.create(nom="Structure existante")
        upload = SimpleUploadedFile(
            "structures.csv",
            b"NOM,email\nStructure invalide,adresse-invalide\n",
            content_type="text/csv",
        )

        response = self.client.post(
            reverse("dashboard:import_data"),
            {"fichier": upload, "ecraser": "on"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Structure.objects.filter(nom="Structure existante").exists())
        self.assertFalse(Structure.objects.filter(nom="Structure invalide").exists())

    def test_dashboard_uses_local_frontend_dependencies(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard:home"))

        self.assertContains(response, "/static/css/tailwind.css")
        self.assertContains(response, "/static/vendor/inter/inter.css")
        self.assertNotContains(response, "cdn.tailwindcss.com")
        self.assertNotContains(response, "fonts.googleapis.com")


class StructureMapSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.user)

    def test_map_serializes_untrusted_text_with_json_script(self):
        Structure.objects.create(
            nom="</script><script>alert(1)</script>",
            latitude=50.0,
            longitude=4.0,
        )

        response = self.client.get(reverse("structures:carte"))

        self.assertContains(response, 'id="structures-data"', html=False)
        self.assertNotContains(response, "</script><script>alert(1)</script>", html=False)
        self.assertContains(response, "\\u003C/script\\u003E", html=False)

    def test_map_uses_local_frontend_dependencies(self):
        Structure.objects.create(nom="Structure", latitude=50.0, longitude=4.0)

        response = self.client.get(reverse("structures:carte"))

        self.assertContains(response, "/static/vendor/leaflet/leaflet.js")
        self.assertNotContains(response, "unpkg.com")

    def test_map_json_data_block_carries_csp_nonce(self):
        Structure.objects.create(nom="Structure", latitude=50.0, longitude=4.0)

        response = self.client.get(reverse("structures:carte"))

        policy = response["Content-Security-Policy"]
        match = re.search(r"'nonce-([A-Za-z0-9_-]+)'", policy)
        self.assertIsNotNone(match)
        self.assertContains(
            response,
            f'id="structures-data" type="application/json" nonce="{match.group(1)}"',
            html=False,
        )


class HealthCheckTests(TestCase):
    def test_health_endpoint_exposes_only_liveness(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})


class SQLiteBackupTests(TestCase):
    def test_backup_is_consistent_and_verifiable(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_directory = root / "source"
            backup_directory = root / "backups"
            source_directory.mkdir()
            source = source_directory / "database.sqlite3"
            with closing(sqlite3.connect(source)) as connection:
                connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
                connection.execute("INSERT INTO example VALUES ('avant')")
                connection.commit()

            result = create_sqlite_backup(source, backup_directory)

            verify_sqlite_database(result.path)
            self.assertEqual(len(result.sha256), 64)
            with closing(sqlite3.connect(result.path)) as connection:
                self.assertEqual(
                    connection.execute("SELECT value FROM example").fetchone(),
                    ("avant",),
                )


class PublicStructureViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="visiteur@example.test",
            email="visiteur@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.user)
        self.commune = Commune.objects.create(nom="Exemple", code_postal="75001")
        self.autre_commune = Commune.objects.create(nom="Autre", code_postal="75002")
        UserCommune.objects.create(user=self.user, commune=self.commune)
        self.type_crèche = TypeStructure.objects.create(nom="Crèche collective")
        self.visible = Structure.objects.create(
            nom="Crèche Visible",
            afficher=True,
            commune=self.commune,
            type=self.type_crèche,
            places_disponibles=3,
            places_complet=False,
            places_non_communique=False,
        )
        self.hidden = Structure.objects.create(nom="Masquée", afficher=False)

    def test_list_shows_only_visible_structures_in_scope(self):
        Structure.objects.create(nom="Hors périmètre", afficher=True, commune=self.autre_commune)

        response = self.client.get(reverse("structures:liste"))

        self.assertContains(response, "Crèche Visible")
        self.assertNotContains(response, "Masquée")
        self.assertContains(response, "Hors périmètre")

    def test_superuser_sees_all_visible_structures(self):
        admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(admin)
        Structure.objects.create(nom="Hors périmètre", afficher=True, commune=self.autre_commune)

        response = self.client.get(reverse("structures:liste"))

        self.assertContains(response, "Crèche Visible")
        self.assertContains(response, "Hors périmètre")

    def test_list_commune_dropdown_is_scoped(self):
        response = self.client.get(reverse("structures:liste"))

        self.assertContains(response, "Exemple")
        self.assertContains(response, "Autre")

    def test_list_filters_by_commune(self):
        Structure.objects.create(
            nom="Autre commune", afficher=True, commune=self.autre_commune
        )

        response = self.client.get(reverse("structures:liste"), {"commune": self.commune.pk})

        self.assertContains(response, "Crèche Visible")
        self.assertNotContains(response, "Autre commune")

    def test_list_filters_by_type(self):
        micro = TypeStructure.objects.create(nom="Micro-crèche")
        Structure.objects.create(nom="Micro X", afficher=True, type=micro)

        response = self.client.get(reverse("structures:liste"), {"type": self.type_crèche.pk})

        self.assertContains(response, "Crèche Visible")
        self.assertNotContains(response, "Micro X")

    def test_list_filters_by_available_places(self):
        Structure.objects.create(nom="Complet X", afficher=True, places_complet=True)

        response = self.client.get(reverse("structures:liste"), {"places": "oui"})

        self.assertEqual(list(response.context["structure_list"]), [self.visible])
        self.assertNotContains(response, "Complet X")

    def test_detail_hides_unpublished_structure(self):
        response = self.client.get(reverse("structures:detail", args=[self.hidden.pk]))

        self.assertEqual(response.status_code, 404)

    def test_detail_shows_published_structure(self):
        response = self.client.get(reverse("structures:detail", args=[self.visible.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crèche Visible")

    def test_detail_outside_scope_is_404(self):
        outside = Structure.objects.create(
            nom="Hors périmètre", afficher=True, commune=self.autre_commune
        )

        response = self.client.get(reverse("structures:detail", args=[outside.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hors périmètre")

    def test_map_only_shows_geolocated_visible_structures_in_scope(self):
        Structure.objects.create(
            nom="Geo Test", afficher=True, latitude=50.0, longitude=4.0, commune=self.commune
        )
        Structure.objects.create(
            nom="Geo Hors périmètre",
            afficher=True,
            latitude=51.0,
            longitude=4.0,
            commune=self.autre_commune,
        )

        response = self.client.get(reverse("structures:carte"))

        self.assertContains(response, "Geo Test")
        self.assertContains(response, "Geo Hors")
        self.assertNotContains(response, "Masquée")

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()

        for url in (
            reverse("structures:liste"),
            reverse("structures:carte"),
            reverse("structures:detail", args=[self.visible.pk]),
        ):
            response = self.client.get(url)

            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("login"), response.url)
            self.assertIn(url, response.url)


class DashboardSidebarTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )
        self.collaborator = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )

    def test_collaborator_sidebar_hides_admin_sections(self):
        self.client.force_login(self.collaborator)

        response = self.client.get(reverse("dashboard:structure_list"))

        self.assertContains(response, "Structures")
        for label in (
            "Utilisateurs",
            "Demandes d'inscription",
            "Notifications",
            "Sauvegardes",
        ):
            self.assertNotContains(response, label)

    def test_superuser_sidebar_shows_admin_sections(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard:structure_list"))

        for label in (
            "Utilisateurs",
            "Demandes d'inscription",
            "Notifications",
            "Sauvegardes",
        ):
            self.assertContains(response, label)


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="normal@example.test",
            email="normal@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_non_superuser_can_access_dashboard_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.status_code, 200)


class DashboardPasswordChangeTests(TestCase):
    current_password = "Un-mot-de-passe-tres-long-2026"
    new_password = "Un-nouveau-mot-de-passe-tres-long-2027"

    def setUp(self):
        self.user = User.objects.create_user(
            username="agent@example.test",
            email="agent@example.test",
            password=self.current_password,
        )
        self.client.force_login(self.user)

    def test_page_highlights_password_navigation(self):
        response = self.client.get(reverse("dashboard:password_change"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_tab"], "password")

    def test_invalid_current_password_marks_the_field_as_invalid(self):
        response = self.client.post(
            reverse("dashboard:password_change"),
            {
                "old_password": "Mot-de-passe-incorrect",
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("old_password", response.context["form"].errors)
        self.assertContains(response, 'aria-invalid="true"')

    def test_regular_user_changes_password_and_returns_home(self):
        response = self.client.post(
            reverse("dashboard:password_change"),
            {
                "old_password": self.current_password,
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("home"))
        self.assertContains(response, "Votre mot de passe a bien été modifié.")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_superuser_changes_password_and_returns_to_dashboard(self):
        admin = User.objects.create_superuser(
            username="admin-password@example.test",
            email="admin-password@example.test",
            password=self.current_password,
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse("dashboard:password_change"),
            {
                "old_password": self.current_password,
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )

        self.assertRedirects(response, reverse("dashboard:home"))


class DashboardStructureListTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin-structures@example.test",
            email="admin-structures@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)
        self.commune = Commune.objects.create(nom="Testville", code_postal="75001")
        self.type = TypeStructure.objects.create(nom="Accueil de loisirs")
        self.structure = Structure.objects.create(
            nom="Les Explorateurs",
            commune=self.commune,
            type=self.type,
        )
        Structure.objects.create(nom="Autre structure")

    def test_list_exposes_clear_filters_and_selection_controls(self):
        response = self.client.get(reverse("dashboard:structure_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rechercher dans l’annuaire")
        self.assertContains(response, "Nom ou mot-clé")
        self.assertContains(response, "Sélectionner la page")
        self.assertContains(response, 'id="batch-delete" disabled')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, f"Modifier {self.structure.nom}")

    def test_filters_reduce_results_and_remain_selected(self):
        response = self.client.get(
            reverse("dashboard:structure_list"),
            {"q": "Explorateurs", "type": self.type.pk, "commune": self.commune.pk},
        )

        self.assertEqual(list(response.context["structure_list"]), [self.structure])
        self.assertContains(response, 'value="Explorateurs"')
        self.assertContains(response, f'value="{self.type.pk}" selected')
        self.assertContains(response, f'value="{self.commune.pk}" selected')
        self.assertContains(response, "structure trouvée")
        self.assertContains(response, "avec ces critères")

    def test_sort_links_start_ascending_and_expose_current_direction(self):
        response = self.client.get(reverse("dashboard:structure_list"))

        self.assertContains(response, 'aria-sort="ascending"')
        self.assertContains(response, "?o=type.asc")
        self.assertContains(response, "Trier par Type, ordre croissant")


class DashboardOverviewAndReferenceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin-overview@example.test",
            email="admin-overview@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)
        self.commune = Commune.objects.create(nom="Testville", code_postal="75001")
        self.other_commune = Commune.objects.create(
            nom="Autreville",
            code_postal="75002",
        )
        self.type = TypeStructure.objects.create(nom="Accueil de loisirs")
        self.other_type = TypeStructure.objects.create(nom="Crèche")
        self.visible = Structure.objects.create(
            nom="Les Explorateurs",
            afficher=True,
            commune=self.commune,
            type=self.type,
            places_disponibles=3,
            nb_places_total=20,
            date_mise_a_jour_monenfant=date(2026, 7, 1),
            horaires=[{"jour": "mercredi", "ferme": False}],
        )
        Structure.objects.create(
            nom="Structure masquée",
            afficher=False,
            commune=self.commune,
            type=self.type,
            places_non_communique=True,
            nb_places_total=100,
            date_mise_a_jour_monenfant=date(2025, 1, 1),
        )
        Structure.objects.create(
            nom="Structure complète",
            afficher=True,
            commune=self.other_commune,
            type=self.other_type,
            places_complet=True,
            nb_places_total=10,
            date_mise_a_jour_monenfant=date(2026, 4, 1),
        )

    def test_commune_search_filters_and_exposes_annotated_structure_count(self):
        with CaptureQueriesContext(connection) as captured_queries:
            response = self.client.get(
                reverse("dashboard:commune_list"),
                {"q": "75001"},
            )

        self.assertEqual(list(response.context["communes"]), [self.commune])
        commune = response.context["communes"][0]
        self.assertEqual(commune.structure_count, 2)
        self.assertContains(response, "Nom ou code postal")
        self.assertContains(response, "2 structures")
        self.assertContains(response, f"Modifier {self.commune.nom}")
        self.assertNotContains(response, self.other_commune.nom)
        per_row_count_queries = [
            query
            for query in captured_queries.captured_queries
            if 'FROM "structures_structure"' in query["sql"]
        ]
        self.assertEqual(per_row_count_queries, [])

    def test_type_search_filters_and_exposes_annotated_structure_count(self):
        response = self.client.get(
            reverse("dashboard:type_list"),
            {"q": "loisirs"},
        )

        self.assertEqual(list(response.context["types"]), [self.type])
        type_ = response.context["types"][0]
        self.assertEqual(type_.structure_count, 2)
        self.assertContains(response, "Rechercher un type")
        self.assertContains(response, "2 structures")
        self.assertNotContains(response, self.other_type.nom)

    def test_dashboard_keeps_actions_indicators_and_three_charts(self):
        response = self.client.get(reverse("dashboard:home"))

        self.assertEqual(response.context["total_structures"], 3)
        self.assertEqual(response.context["total_visible"], 2)
        self.assertEqual(response.context["total_hidden"], 1)
        self.assertEqual(response.context["total_non_communique"], 1)
        self.assertEqual(response.context["total_complets"], 1)
        self.assertEqual(response.context["total_places"], 3)
        self.assertEqual(response.context["offer_stats"]["capacity_total"], 30)
        self.assertEqual(response.context["offer_stats"]["capacity_average"], 15.0)
        self.assertEqual(response.context["types_count"][0]["total"], 1)
        self.assertContains(response, "Que souhaitez-vous faire ?")
        self.assertContains(response, "Dernières modifications")
        self.assertContains(response, self.visible.nom)
        self.assertContains(response, "/static/vendor/chart.js/chart.umd.js")
        self.assertContains(response, 'id="chart-evolution"')
        self.assertContains(response, 'id="chart-types"')
        self.assertContains(response, 'id="chart-communes"')
        self.assertContains(response, 'id="chart-capacity-types"')
        self.assertContains(response, 'id="chart-capacity-communes"')
        self.assertContains(response, 'id="chart-opening-days"')
        self.assertContains(response, "Fraîcheur des données source")
        self.assertContains(response, "Qualité des fiches")
        self.assertContains(response, "Afficher les données mensuelles")
        self.assertContains(response, "Afficher les capacités par type")
        self.assertContains(response, "Afficher les données par jour")
        policy = response["Content-Security-Policy"]
        nonce_match = re.search(r"'nonce-([A-Za-z0-9_-]+)'", policy)
        self.assertIsNotNone(nonce_match)
        self.assertContains(
            response,
            f'id="chart-capacity-type-labels" type="application/json" nonce="{nonce_match.group(1)}"',
            html=False,
        )
        self.assertEqual(len(response.context["chart_month_data"]), 12)
        self.assertEqual(
            len(response.context["chart_months"]),
            len(response.context["chart_month_counts"]),
        )
        self.assertContains(response, 'aria-current="page"')

    def test_dashboard_query_count_is_stable_when_structures_are_added(self):
        with CaptureQueriesContext(connection) as initial_queries:
            self.client.get(reverse("dashboard:home"))
        Structure.objects.bulk_create(
            [
                Structure(
                    nom=f"Structure supplémentaire {index}",
                    afficher=True,
                    commune=self.commune,
                    type=self.type,
                )
                for index in range(12)
            ]
        )

        with CaptureQueriesContext(connection) as expanded_queries:
            self.client.get(reverse("dashboard:home"))

        self.assertEqual(len(expanded_queries), len(initial_queries))


class StructureFormErrorDisplayTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin-erreurs@example.test",
            email="admin-erreurs@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)
        self.commune = Commune.objects.create(nom="Testville", code_postal="75001")
        self.horaires = json.dumps([{"jour": "lundi", "ferme": True}])

    def _post_invalid(self, **extra):
        data = {"nom": "Structure invalide", "horaires": self.horaires}
        data.update(extra)
        return self.client.post(reverse("dashboard:structure_add"), data)

    def test_negative_age_error_is_displayed(self):
        response = self._post_invalid(age_min="-3", age_min_unite="ans")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "L&#x27;âge ne peut pas être négatif.", html=False)
        self.assertFalse(Structure.objects.filter(nom="Structure invalide").exists())

    def test_max_below_min_error_is_displayed(self):
        response = self._post_invalid(
            age_min="5", age_min_unite="ans", age_max="1", age_max_unite="ans"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "L&#x27;âge maximum doit être supérieur ou égal à l&#x27;âge minimum.",
            html=False,
        )

    def test_places_exceeding_capacity_error_is_displayed(self):
        response = self._post_invalid(places_disponibles="20", nb_places_total="10")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Le nombre de places disponibles ne peut pas dépasser la capacité totale.",
            html=False,
        )

    def test_invalid_email_error_is_displayed(self):
        response = self._post_invalid(email="pas-un-email")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "adresse de courriel valide", html=False)

    def test_conflicting_places_statuses_error_is_displayed(self):
        response = self._post_invalid(places_complet="on", places_non_communique="on")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Une structure ne peut pas être à la fois complète et non communiquée.",
            html=False,
        )

    def test_commune_selection_is_preserved_after_error(self):
        response = self._post_invalid(
            commune=str(self.commune.pk), age_min="-3", age_min_unite="ans"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<option value="{self.commune.pk}" selected>{self.commune.code_postal} {self.commune.nom}</option>',
            html=False,
        )


class StructureScheduleEditorTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin-horaires@example.test",
            email="admin-horaires@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)

    def test_form_exposes_timeslider_widget_full_width(self):
        response = self.client.get(reverse("dashboard:structure_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="hours-picker"')
        self.assertContains(response, 'css/timeslider.css')
        self.assertContains(response, 'js/timeslider.js')
        self.assertContains(response, 'name="horaires"')
        self.assertContains(response, 'class="w-full"')
        self.assertContains(response, "xl:grid-cols-2")
        self.assertNotContains(response, 'type="time"')

    def test_schedule_json_is_saved_without_changing_its_shape(self):
        schedule = [
            {
                "jour": day,
                "ferme": day == "dimanche",
                "ouverture": "08:00",
                "fermeture": "18:00",
            }
            for day in ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        ]

        response = self.client.post(
            reverse("dashboard:structure_add"),
            {"nom": "Structure horaires", "horaires": json.dumps(schedule)},
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        structure = Structure.objects.get(nom="Structure horaires")
        self.assertEqual(structure.horaires, schedule)

    def test_existing_schedule_is_available_when_editing(self):
        schedule = [
            {"jour": "lundi", "ferme": False, "ouverture": "08:07", "fermeture": "17:53"},
            {"jour": "mardi", "ferme": True, "ouverture": "07:30", "fermeture": "18:00"},
        ]
        structure = Structure.objects.create(nom="Structure à modifier", horaires=schedule)

        response = self.client.get(reverse("dashboard:structure_edit", args=[structure.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="horaires"')
        self.assertContains(response, "08:07")
        self.assertContains(response, "17:53")


class StructureFlashMessageTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin-flash@example.test",
            email="admin-flash@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)
        self.horaires = json.dumps([{"jour": "lundi", "ferme": True}])

    def test_create_structure_shows_flash_message(self):
        response = self.client.post(
            reverse("dashboard:structure_add"),
            {"nom": "Crèche flash", "horaires": self.horaires},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertContains(response, "La structure « Crèche flash » a été créée.")

    def test_update_structure_shows_flash_message(self):
        structure = Structure.objects.create(nom="Avant")

        response = self.client.post(
            reverse("dashboard:structure_edit", args=[structure.pk]),
            {"nom": "Après", "horaires": self.horaires},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertContains(response, "La structure « Après » a été mise à jour.")

    def test_delete_structure_shows_flash_message(self):
        structure = Structure.objects.create(nom="À supprimer")

        response = self.client.post(
            reverse("dashboard:structure_delete", args=[structure.pk]),
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertContains(response, "La structure « À supprimer » a été supprimée.")


class DashboardCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password="Un-mot-de-passe-tres-long-2026",
        )
        self.client.force_login(self.admin)

    def test_commune_create(self):
        response = self.client.post(
            reverse("dashboard:commune_add"),
            {"nom": "Testville", "code_postal": "75001"},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:commune_list"))
        self.assertTrue(Commune.objects.filter(nom="Testville").exists())
        self.assertContains(response, "La commune « Testville » a été créée.")

    def test_commune_update(self):
        commune = Commune.objects.create(nom="Avant", code_postal="75001")

        response = self.client.post(
            reverse("dashboard:commune_edit", args=[commune.pk]),
            {"nom": "Après", "code_postal": "75002"},
        )

        self.assertRedirects(response, reverse("dashboard:commune_list"))
        commune.refresh_from_db()
        self.assertEqual(commune.nom, "Après")

    def test_commune_delete(self):
        commune = Commune.objects.create(nom="À supprimer", code_postal="75001")

        response = self.client.post(reverse("dashboard:commune_delete", args=[commune.pk]))

        self.assertRedirects(response, reverse("dashboard:commune_list"))
        self.assertFalse(Commune.objects.filter(pk=commune.pk).exists())

    def test_type_create(self):
        response = self.client.post(
            reverse("dashboard:type_add"),
            {"nom": "Micro-crèche"},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:type_list"))
        self.assertTrue(TypeStructure.objects.filter(nom="Micro-crèche").exists())
        self.assertContains(response, "Le type « Micro-crèche » a été créé.")

    def test_type_update(self):
        type_ = TypeStructure.objects.create(nom="Avant")

        response = self.client.post(
            reverse("dashboard:type_edit", args=[type_.pk]), {"nom": "Après"}
        )

        self.assertRedirects(response, reverse("dashboard:type_list"))
        type_.refresh_from_db()
        self.assertEqual(type_.nom, "Après")

    def test_type_delete(self):
        type_ = TypeStructure.objects.create(nom="À supprimer")

        response = self.client.post(reverse("dashboard:type_delete", args=[type_.pk]))

        self.assertRedirects(response, reverse("dashboard:type_list"))
        self.assertFalse(TypeStructure.objects.filter(pk=type_.pk).exists())

    def test_batch_delete_removes_selected_and_logs(self):
        first = Structure.objects.create(nom="Première")
        second = Structure.objects.create(nom="Seconde")

        response = self.client.post(
            reverse("dashboard:structure_batch"),
            {"ids": [str(first.pk), str(second.pk)], "action": "delete"},
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertFalse(Structure.objects.filter(pk__in=[first.pk, second.pk]).exists())
        self.assertContains(response, "2 structures supprimées.")
        audit_entry = AuditLog.objects.get(action="batch")
        self.assertEqual(audit_entry.changes["_count"], 2)

    def test_structure_delete_confirms_which_entry_was_removed(self):
        structure = Structure.objects.create(nom="Structure à supprimer")

        response = self.client.post(
            reverse("dashboard:structure_delete", args=[structure.pk]),
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertContains(
            response,
            "La structure « Structure à supprimer » a été supprimée.",
        )


class CollaboratorStructureScopeTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )
        self.collab = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
            first_name="Camille",
            last_name="Durand",
        )
        self.commune_a = Commune.objects.create(nom="Marseille", code_postal="13001")
        self.commune_b = Commune.objects.create(nom="Aix-en-Provence", code_postal="13100")
        UserCommune.objects.create(user=self.collab, commune=self.commune_a)
        self.structure_a = Structure.objects.create(nom="Crèche A", commune=self.commune_a)
        self.structure_b = Structure.objects.create(nom="Crèche B", commune=self.commune_b)

    def test_collaborator_only_sees_structures_of_linked_communes(self):
        self.client.force_login(self.collab)

        response = self.client.get(reverse("dashboard:structure_list"))

        self.assertEqual(list(response.context["object_list"]), [self.structure_a, self.structure_b])

    def test_collaborator_can_edit_structure_of_linked_commune(self):
        self.client.force_login(self.collab)

        response = self.client.get(reverse("dashboard:structure_edit", args=[self.structure_a.pk]))

        self.assertEqual(response.status_code, 200)

    def test_collaborator_cannot_edit_structure_outside_scope(self):
        self.client.force_login(self.collab)

        response = self.client.get(reverse("dashboard:structure_edit", args=[self.structure_b.pk]))

        self.assertEqual(response.status_code, 404)

    def test_collaborator_cannot_delete_structure_outside_scope(self):
        self.client.force_login(self.collab)

        response = self.client.post(reverse("dashboard:structure_delete", args=[self.structure_b.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Structure.objects.filter(pk=self.structure_b.pk).exists())

    def test_collaborator_cannot_create_structure_outside_communes(self):
        self.client.force_login(self.collab)
        horaires = json.dumps([{"jour": "lundi", "ferme": True}])

        response = self.client.post(
            reverse("dashboard:structure_add"),
            {"nom": "Hors périmètre", "commune": str(self.commune_b.pk), "horaires": horaires},
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFormError(form, "commune", "Sélectionnez un choix valide. Ce choix ne fait pas partie de ceux disponibles.")
        self.assertFalse(Structure.objects.filter(nom="Hors périmètre").exists())

    def test_collaborator_can_create_structure_in_linked_commune(self):
        self.client.force_login(self.collab)
        horaires = json.dumps([{"jour": "lundi", "ferme": True}])

        response = self.client.post(
            reverse("dashboard:structure_add"),
            {"nom": "Crèche C", "commune": str(self.commune_a.pk), "horaires": horaires},
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertTrue(Structure.objects.filter(nom="Crèche C", commune=self.commune_a).exists())

    def test_batch_delete_ignores_structures_outside_scope(self):
        self.client.force_login(self.collab)

        response = self.client.post(
            reverse("dashboard:structure_batch"),
            {
                "ids": [str(self.structure_a.pk), str(self.structure_b.pk)],
                "action": "delete",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("dashboard:structure_list"))
        self.assertFalse(Structure.objects.filter(pk=self.structure_a.pk).exists())
        self.assertTrue(Structure.objects.filter(pk=self.structure_b.pk).exists())

    def test_superuser_sees_all_structures(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard:structure_list"))

        self.assertEqual(response.context["object_list"].count(), 2)


class BackupServiceTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source_dir = root / "source"
        self.source_dir.mkdir()
        self.source = self.source_dir / "database.sqlite3"
        with closing(sqlite3.connect(self.source)) as connection:
            connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
            connection.execute("INSERT INTO example VALUES ('avant')")
            connection.commit()
        self.backup_dir = root / "backups"

    def _create_backup(self, environment="production"):
        return create_sqlite_backup(self.source, self.backup_dir, environment=environment)

    def test_list_sorted_and_catalog_status(self):
        first = self._create_backup()
        second = self._create_backup()

        backups = list_sqlite_backups(self.backup_dir)

        self.assertEqual([backup.name for backup in backups], [second.path.name, first.path.name])
        self.assertIsNone(backups[0].sha256)
        self.assertFalse(backups[0].verified)

        sha256, size = mark_backup_verified(self.backup_dir, second.path.name)

        self.assertEqual(len(sha256), 64)
        self.assertEqual(size, second.size)
        verified = list_sqlite_backups(self.backup_dir)
        self.assertTrue(verified[0].verified)
        self.assertEqual(verified[0].sha256, sha256)

    def test_purge_keeps_only_last_n_and_ignores_unrelated_files(self):
        for _ in range(4):
            self._create_backup()
        self._create_backup(environment="dev")
        unrelated = self.backup_dir / "note.txt"
        unrelated.write_text("contenu", "utf-8")
        fake_name = self.backup_dir / "bdd-pe-quelquechose.sqlite3"
        fake_name.write_text("pas une sauvegarde", "utf-8")

        removed = purge_sqlite_backups(self.backup_dir, keep=2)

        self.assertEqual(removed, 3)
        remaining = [backup.name for backup in list_sqlite_backups(self.backup_dir)]
        self.assertEqual(len(remaining), 2)
        self.assertTrue(unrelated.exists())
        self.assertTrue(fake_name.exists())

    def test_delete_removes_file_and_catalog_entry(self):
        created = self._create_backup()
        mark_backup_verified(self.backup_dir, created.path.name)

        delete_sqlite_backup(self.backup_dir, created.path.name)

        self.assertFalse(created.path.exists())
        self.assertEqual(list_sqlite_backups(self.backup_dir), [])

    def test_delete_refuses_traversal_and_invalid_names(self):
        created = self._create_backup()
        for name in (
            "../source/database.sqlite3",
            str(self.source.resolve()),
            "bdd-pe-prod-2026.sqlite3",
            "bdd-pe-prod/20260818T000000000000Z.sqlite3",
            "",
        ):
            with self.assertRaises(SQLiteBackupError):
                delete_sqlite_backup(self.backup_dir, name)
        self.assertTrue(created.path.exists())

    def test_delete_refuses_symlink(self):
        outside = self.backup_dir.parent / "cible.sqlite3"
        outside.write_bytes(b"x")
        link = self.backup_dir / "bdd-pe-prod-20260818T000000000000Z.sqlite3"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks non supportés sur cette machine.")
        with self.assertRaises(SQLiteBackupError):
            delete_sqlite_backup(self.backup_dir, link.name)
        self.assertTrue(outside.exists())

    def test_lock_blocks_second_backup(self):
        self.backup_dir.mkdir()
        with backup_lock(self.backup_dir):
            with self.assertRaises(SQLiteBackupError):
                run_backup(
                    self.source,
                    self.backup_dir,
                    keep=7,
                    environment="production",
                )
        run_backup(self.source, self.backup_dir, keep=7, environment="production")
        self.assertEqual(len(list_sqlite_backups(self.backup_dir)), 1)

    def test_stale_lock_is_removed(self):
        self.backup_dir.mkdir()
        lock_path = self.backup_dir / ".bddpe-backup.lock"
        lock_path.write_text("1", "utf-8")
        old_time = timezone.now().timestamp() - 3600
        os.utime(lock_path, (old_time, old_time))

        run_backup(self.source, self.backup_dir, keep=7, environment="production")

        self.assertEqual(len(list_sqlite_backups(self.backup_dir)), 1)

    def test_insufficient_disk_space_is_refused(self):
        with mock.patch(
            "structures.services.sqlite_backup.shutil.disk_usage",
            return_value=shutil.disk_usage(".")._replace(free=1024),
        ):
            with self.assertRaises(SQLiteBackupError):
                run_backup(
                    self.source,
                    self.backup_dir,
                    keep=7,
                    environment="production",
                )
        self.assertEqual(list_sqlite_backups(self.backup_dir), [])

    def test_corrupted_catalog_is_ignored(self):
        self.backup_dir.mkdir()
        (self.backup_dir / ".bddpe-backups.json").write_text(
            "{{{pas du json", "utf-8"
        )

        self.assertEqual(list_sqlite_backups(self.backup_dir), [])

    def test_run_backup_verifies_and_applies_rotation(self):
        for _ in range(3):
            run_backup(
                self.source,
                self.backup_dir,
                keep=2,
                environment="production",
            )

        backups = list_sqlite_backups(self.backup_dir)
        self.assertEqual(len(backups), 2)
        self.assertTrue(all(backup.verified for backup in backups))
        self.assertTrue(all(backup.sha256 for backup in backups))
        verify_sqlite_database(self.backup_dir / backups[0].name)


class BackupDashboardTests(TestCase):
    password = "Un-mot-de-passe-tres-long-2026"

    def setUp(self):
        caches["ratelimit"].clear()
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.backup_dir = root / "backups"
        self.backup_dir.mkdir()
        self.source = root / "source.sqlite3"
        with closing(sqlite3.connect(self.source)) as connection:
            connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
            connection.commit()
        self.admin = User.objects.create_superuser(
            username="admin@example.test",
            email="admin@example.test",
            password=self.password,
        )
        self.collaborator = User.objects.create_user(
            username="collab@example.test",
            email="collab@example.test",
            password=self.password,
        )
        self.override = override_settings(
            BACKUP_DIR=str(self.backup_dir),
            BACKUP_RETENTION=7,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(self.source),
                    "OPTIONS": {"timeout": 20},
                }
            },
        )
        self.override.enable()
        self.addCleanup(self.override.disable)

    def _create_backup_file(self):
        return create_sqlite_backup(
            self.source, self.backup_dir, environment="prod"
        )

    def test_page_requires_superuser(self):
        self.client.force_login(self.collaborator)

        response = self.client.get(reverse("dashboard:backup_list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_actions_require_superuser(self):
        self.client.force_login(self.collaborator)

        response = self.client.post(reverse("dashboard:backup_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_manual_backup_creates_valid_file_and_audit_entry(self):
        self.client.force_login(self.admin)

        response = self.client.post(reverse("dashboard:backup_create"))

        self.assertRedirects(response, reverse("dashboard:backup_list"))
        backups = list_sqlite_backups(self.backup_dir)
        self.assertEqual(len(backups), 1)
        self.assertTrue(backups[0].verified)
        verify_sqlite_database(self.backup_dir / backups[0].name)
        self.assertTrue(
            AuditLog.objects.filter(
                user=self.admin,
                action="create",
                model_name="BackupSQLite",
                object_repr=backups[0].name,
            ).exists()
        )

    def test_verify_marks_backup_as_verified(self):
        created = self._create_backup_file()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:backup_verify", args=[created.path.name])
        )

        self.assertRedirects(response, reverse("dashboard:backup_list"))
        verified = list_sqlite_backups(self.backup_dir)[0]
        self.assertTrue(verified.verified)
        self.assertEqual(len(verified.sha256), 64)

    def test_delete_confirm_page_and_post(self):
        created = self._create_backup_file()
        self.client.force_login(self.admin)

        confirm = self.client.get(
            reverse("dashboard:backup_delete", args=[created.path.name])
        )
        self.assertEqual(confirm.status_code, 200)

        response = self.client.post(
            reverse("dashboard:backup_delete", args=[created.path.name])
        )

        self.assertRedirects(response, reverse("dashboard:backup_list"))
        self.assertFalse(created.path.exists())
        self.assertTrue(
            AuditLog.objects.filter(
                user=self.admin,
                action="delete",
                model_name="BackupSQLite",
                object_repr=created.path.name,
            ).exists()
        )

    def test_delete_refuses_invalid_name_without_side_effect(self):
        created = self._create_backup_file()
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse("dashboard:backup_delete", args=[".."])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(created.path.exists())

    def test_csrf_is_enforced_on_mutations(self):
        strict_client = Client(enforce_csrf_checks=True)
        strict_client.force_login(self.admin)

        response = strict_client.post(reverse("dashboard:backup_create"))

        self.assertEqual(response.status_code, 403)

    def test_create_is_rate_limited(self):
        self.client.force_login(self.admin)
        for _ in range(12):
            self.client.post(reverse("dashboard:backup_create"))

        response = self.client.post(reverse("dashboard:backup_create"))

        self.assertEqual(response.status_code, 403)

    def test_confirm_page_for_unknown_backup_redirects(self):
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "dashboard:backup_delete",
                args=["bdd-pe-prod-20260818T000000000000Z.sqlite3"],
            )
        )

        self.assertRedirects(response, reverse("dashboard:backup_list"))


class BackupCommandTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / "source.sqlite3"
        with closing(sqlite3.connect(self.source)) as connection:
            connection.execute("CREATE TABLE example (value TEXT NOT NULL)")
            connection.commit()
        self.backup_dir = root / "backups"

    def test_command_uses_backup_dir_and_keep(self):
        with override_settings(
            BACKUP_DIR=str(self.backup_dir),
            BACKUP_RETENTION=2,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(self.source),
                    "OPTIONS": {"timeout": 20},
                }
            },
        ):
            call_command("backup_sqlite")
            call_command("backup_sqlite")
            call_command("backup_sqlite")

            backups = list_sqlite_backups(self.backup_dir)

            self.assertEqual(len(backups), 2)

    def test_command_rejects_invalid_keep(self):
        with override_settings(
            BACKUP_DIR=str(self.backup_dir),
            BACKUP_RETENTION=2,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(self.source),
                    "OPTIONS": {"timeout": 20},
                }
            },
        ):
            from django.core.management.base import CommandError

            with self.assertRaises(CommandError):
                call_command("backup_sqlite", "--keep", "0")
