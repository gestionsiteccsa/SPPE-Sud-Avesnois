from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from structures.services.sqlite_backup import (
    SQLiteBackupError,
    run_backup,
)


class Command(BaseCommand):
    help = (
        "Crée une sauvegarde cohérente de la base SQLite, vérifie son intégrité "
        "et applique la rotation de rétention"
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "destination",
            nargs="?",
            type=Path,
            help="Répertoire privé de destination (défaut : BACKUP_DIR)",
        )
        parser.add_argument(
            "--keep",
            type=int,
            default=None,
            help="Nombre de sauvegardes conservées (défaut : BACKUP_RETENTION)",
        )

    def handle(self, *args, **options) -> None:
        destination = options["destination"] or Path(settings.BACKUP_DIR)
        keep = (
            options["keep"]
            if options["keep"] is not None
            else settings.BACKUP_RETENTION
        )
        if keep < 1:
            raise CommandError("--keep doit être au moins égal à 1.")
        source = Path(settings.DATABASES["default"]["NAME"])
        try:
            result = run_backup(
                source,
                destination,
                keep=keep,
                environment=settings.ENVIRONMENT,
            )
        except SQLiteBackupError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                f"Sauvegarde créée : {result.path.name} "
                f"({result.size} octets, sha256={result.sha256})"
            )
        )
