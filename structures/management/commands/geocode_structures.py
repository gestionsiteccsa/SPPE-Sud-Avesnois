from django.core.management.base import BaseCommand

from structures.models import Structure
from structures.services.geocode import geocode_structure


class Command(BaseCommand):
    help = "Renseigne latitude/longitude des structures qui n'en ont pas encore"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simule sans enregistrer en base",
        )

    def handle(self, *args, **options) -> None:
        dry_run = options["dry_run"]
        missing = Structure.objects.filter(
            latitude__isnull=True,
            longitude__isnull=True,
        )
        total = missing.count()
        if total == 0:
            self.stdout.write("Aucune structure sans coordonnées.")
            return

        self.stdout.write(f"{total} structure(s) à géocoder (dry-run={dry_run}).")
        ok = 0
        failures = 0
        for structure in missing.iterator():
            geocode_structure(structure)
            if structure.latitude is not None and structure.longitude is not None:
                ok += 1
                if not dry_run:
                    structure.save(update_fields=["latitude", "longitude"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [OK] {structure.nom_affiche} -> "
                        f"{structure.latitude:.6f}, {structure.longitude:.6f}"
                    )
                )
            else:
                failures += 1
                self.stdout.write(self.style.WARNING(f"  [KO] {structure.nom_affiche} : introuvable"))

        self.stdout.write(
            self.style.SUCCESS(f"Terminé : {ok} géocodée(s), {failures} échec(s).")
        )