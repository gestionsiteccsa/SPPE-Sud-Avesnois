from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from authentication.models import UserCommune
from communes.models import Commune
from structures.models import Structure, TypeStructure


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="agent@example.test",
            email="agent@example.test",
            password="Mot-de-passe-test-2026!",
        )
        self.client.force_login(self.user)
        self.commune = Commune.objects.create(nom="Exemple", code_postal="75001")
        self.autre_commune = Commune.objects.create(nom="Autre", code_postal="75002")
        UserCommune.objects.create(user=self.user, commune=self.commune)
        self.type_crèche = TypeStructure.objects.create(nom="Crèche collective")

    def test_index_counts_only_visible_structures_in_scope(self):
        Structure.objects.create(
            nom="Visible",
            afficher=True,
            commune=self.commune,
            type=self.type_crèche,
            places_disponibles=3,
            places_complet=False,
            places_non_communique=False,
        )
        Structure.objects.create(nom="Masquée", afficher=False)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_structures"], 1)
        self.assertIn(self.commune, response.context["communes"])
        self.assertIn(self.autre_commune, response.context["communes"])

    def test_index_is_scoped_to_linked_communes(self):
        Structure.objects.create(
            nom="Visible A",
            afficher=True,
            commune=self.commune,
            type=self.type_crèche,
        )
        Structure.objects.create(
            nom="Visible B",
            afficher=True,
            commune=self.autre_commune,
            type=self.type_crèche,
        )

        response = self.client.get(reverse("home"))

        self.assertEqual(response.context["total_structures"], 2)
        self.assertIn(self.commune, response.context["communes"])
        self.assertIn(self.autre_commune, response.context["communes"])

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)


class DataProtectionViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="agent@example.test",
            email="agent@example.test",
            password="Mot-de-passe-test-2026!",
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("data_protection"))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("data_protection")}',
        )

    def test_authenticated_user_can_read_data_protection_notice(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("data_protection"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/data_protection.html")
        self.assertContains(response, "Communauté de Communes Sud-Avesnois")
        self.assertContains(response, "200 044 493 00019")
        self.assertContains(response, "contact@cc-sudavesnois.fr")
        self.assertContains(response, "suppression sous 30 jours")
        self.assertContains(response, "12 mois")
        self.assertContains(response, "3 mois")
        self.assertContains(response, "6 mois")
        self.assertContains(response, "Vos droits")
        self.assertContains(response, "https://www.cnil.fr/fr/plaintes")

    def test_data_protection_page_is_not_indexed(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("data_protection"))

        self.assertContains(
            response,
            '<meta name="robots" content="noindex, nofollow">',
            html=True,
        )

    def test_footer_links_to_data_protection_page(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            f'href="{reverse("data_protection")}">Protection des données</a>',
        )
