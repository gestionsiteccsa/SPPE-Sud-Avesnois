from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from structures.services.import_data import ImportDataError, import_rows, read_rows_from_path


class Command(BaseCommand):
    help = "Importe les structures depuis un fichier CSV ou XLSX"

    def add_arguments(self, parser) -> None:
        parser.add_argument("fichier", type=Path, help="Chemin vers le fichier .csv ou .xlsx")
        parser.add_argument(
            "--ecraser",
            action="store_true",
            help="Remplacer les données existantes dans une transaction",
        )

    def handle(self, *args, **options) -> None:
        try:
            rows = read_rows_from_path(options["fichier"])
            count = import_rows(rows, replace=options["ecraser"], actor=None)
        except ImportDataError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS(f"{count} structure(s) importée(s)."))
