import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

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
        parser.add_argument(
            "--export-ko",
            default="",
            help="Chemin CSV pour exporter les adresses introuvables",
        )

    def handle(self, *args, **options) -> None:
        dry_run = options["dry_run"]
        export_ko = (options.get("export_ko") or "").strip()
        missing = Structure.objects.select_related("commune").filter(
            Q(latitude__isnull=True) | Q(longitude__isnull=True),
        )
        total = missing.count()
        if total == 0:
            self.stdout.write("Aucune structure sans coordonnées.")
            return

        self.stdout.write(f"{total} structure(s) à géocoder (dry-run={dry_run}).")
        ok = 0
        failures = 0
        ko_rows = []
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
                commune = structure.commune
                ko_rows.append(
                    {
                        "nom": structure.nom_affiche,
                        "adresse": structure.adresse,
                        "code_postal": commune.code_postal if commune else "",
                        "commune": commune.nom if commune else "",
                        "motif": "introuvable (BAN puis Nominatim)",
                    }
                )
                self.stdout.write(self.style.WARNING(f"  [KO] {structure.nom_affiche} : introuvable"))

        if export_ko and ko_rows:
            with open(export_ko, "w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["nom", "adresse", "code_postal", "commune", "motif"],
                    delimiter=";",
                )
                writer.writeheader()
                writer.writerows(ko_rows)
            self.stdout.write(f"Export des introuvables : {export_ko} ({len(ko_rows)} ligne(s)).")
        elif export_ko:
            self.stdout.write("Aucun introuvable à exporter.")

        self.stdout.write(
            self.style.SUCCESS(f"Terminé : {ok} géocodée(s), {failures} échec(s).")
        )
        if dry_run:
            dated = datetime.now().strftime("%Y-%m-%d")
            self.stdout.write(
                "Pensez à relancer sans --dry-run après sauvegarde "
                f"puis à corriger les KO à la main (export --export-ko geocodage-echecs-{dated}.csv)."
            )