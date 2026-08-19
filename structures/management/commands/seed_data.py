from django.core.management.base import BaseCommand
from django.db import transaction

from communes.models import Commune
from structures.models import AuditLog, Structure, TypeStructure
from structures.services.import_data import import_rows


# Jeu de démonstration entièrement fictif. Toute ressemblance est fortuite.
DATA = [
    {
        "Référencé monenfant.fr": "Non",
        "Date mise à jour": "15/01/2026",
        "NOM": "Crèche des Petits Nuages",
        "Type": "Crèche collective",
        "Tranche d'âge": "10 semaines - 4 ans",
        "Horaires": "Lun-Ven 07h30-18h30",
        "adresse": "1 rue des Exemples",
        "code postal": "00001",
        "commune": "Ville Démonstration",
        "tel": "00 00 00 00 01",
        "email": "contact.creche@example.test",
        "places dispos": "2",
        "nb de places total": "24",
        "Accueil handicap": "Oui",
        "Site web": "https://example.test/petits-nuages",
        "statut": "Démonstration",
        "Nb de professionnel.les": "8",
        "recrutement en cours ?": "Non",
        "OK accueil d'urgence": "Oui",
    },
    {
        "Référencé monenfant.fr": "Non",
        "Date mise à jour": "20/01/2026",
        "NOM": "Micro-crèche Arc-en-ciel",
        "Type": "Micro-crèche",
        "Tranche d'âge": "3 mois - 4 ans",
        "Horaires": "Lun-Ven 08h00-18h00",
        "adresse": "2 avenue Fictive",
        "code postal": "00001",
        "commune": "Ville Démonstration",
        "tel": "00 00 00 00 02",
        "email": "arc-en-ciel@example.test",
        "places dispos": "Complet",
        "nb de places total": "12",
        "Accueil handicap": "Non",
        "Site web": "https://example.test/arc-en-ciel",
        "statut": "Démonstration",
        "Nb de professionnel.les": "5",
        "recrutement en cours ?": "Oui",
        "OK accueil d'urgence": "Non",
    },
    {
        "Référencé monenfant.fr": "Non",
        "Date mise à jour": "02/02/2026",
        "NOM": "Maison d'assistantes Les Étoiles",
        "Type": "Maison d'assistantes maternelles",
        "Tranche d'âge": "non renseigné",
        "Horaires": "Lun-Ven 07h00-19h00",
        "adresse": "3 place Imaginaire",
        "code postal": "00002",
        "commune": "Commune Exemple",
        "tel": "00 00 00 00 03",
        "email": "les-etoiles@example.test",
        "places dispos": "Non communiqué",
        "nb de places total": "16",
        "Accueil handicap": "Oui",
        "statut": "Démonstration",
        "Nb de professionnel.les": "4",
        "OK accueil d'urgence": "Oui",
    },
    {
        "Référencé monenfant.fr": "Non",
        "Date mise à jour": "05/02/2026",
        "NOM": "Relais Petite Enfance Horizon",
        "Type": "Relais petite enfance",
        "Tranche d'âge": "non renseigné",
        "Horaires": "Lun-Ven 09h00-17h00",
        "adresse": "4 boulevard du Prototype",
        "code postal": "00002",
        "commune": "Commune Exemple",
        "tel": "00 00 00 00 04",
        "email": "rpe-horizon@example.test",
        "places dispos": "Non communiqué",
        "Accueil handicap": "",
        "statut": "Démonstration",
    },
    {
        "Référencé monenfant.fr": "Non",
        "Date mise à jour": "08/02/2026",
        "NOM": "Accueil familial des Lucioles",
        "Type": "Crèche familiale",
        "Tranche d'âge": "2 mois - 4 ans",
        "Horaires": "Lun-Sam 06h30-19h30",
        "adresse": "5 impasse des Tests",
        "code postal": "00003",
        "commune": "Bourg Fictif",
        "tel": "00 00 00 00 05",
        "email": "lucioles@example.test",
        "places dispos": "4",
        "nb de places total": "30",
        "Accueil handicap": "Oui",
        "statut": "Démonstration",
        "Nb de professionnel.les": "12",
        "recrutement en cours ?": "Non",
        "OK accueil d'urgence": "Oui",
    },
]


class Command(BaseCommand):
    help = "Initialise la base avec un jeu de démonstration fictif"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--ecraser",
            action="store_true",
            help="Vide les données de démonstration avant l'import",
        )

    def handle(self, *args, **options) -> None:
        with transaction.atomic():
            if options["ecraser"]:
                Structure.objects.all().delete()
                AuditLog.objects.all().delete()
                TypeStructure.objects.all().delete()
                Commune.objects.all().delete()
                self.stdout.write("Données existantes supprimées.")
            count = import_rows(DATA, replace=False, actor=None)
        self.stdout.write(self.style.SUCCESS(f"{count} structures fictives importées."))
