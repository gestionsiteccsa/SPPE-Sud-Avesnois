from django.test import TestCase

from .models import Commune


class CommuneModelTests(TestCase):
    def test_str_shows_postal_code_and_name(self):
        commune = Commune.objects.create(nom="Exemple", code_postal="75001")
        self.assertEqual(str(commune), "75001 Exemple")

    def test_default_ordering_by_name(self):
        Commune.objects.create(nom="Zed", code_postal="75002")
        Commune.objects.create(nom="Alpha", code_postal="75001")

        names = list(Commune.objects.values_list("nom", flat=True))
        self.assertEqual(names, ["Alpha", "Zed"])
