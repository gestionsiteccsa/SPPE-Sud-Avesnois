from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from structures.services.sqlite_backup import SQLiteBackupError, verify_sqlite_database


class Command(BaseCommand):
    help = "Vérifie en lecture seule l'intégrité d'une sauvegarde SQLite"

    def add_arguments(self, parser) -> None:
        parser.add_argument("fichier", type=Path, help="Chemin de la sauvegarde SQLite")

    def handle(self, *args, **options) -> None:
        try:
            verify_sqlite_database(options["fichier"])
        except SQLiteBackupError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(self.style.SUCCESS("Sauvegarde SQLite valide."))
