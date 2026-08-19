from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from structures.models import AuditLog


class Command(BaseCommand):
    help = "Supprime les entrées du journal d'audit plus anciennes que la rétention définie"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--older-than-days",
            type=int,
            default=365,
            help="Âge maximum des entrées conservées, en jours (défaut : 365)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche le nombre d'entrées concernées sans les supprimer",
        )

    def handle(self, *args, **options) -> None:
        cutoff = timezone.now() - timedelta(days=options["older_than_days"])
        queryset = AuditLog.objects.filter(timestamp__lt=cutoff)
        count = queryset.count()
        if options["dry_run"]:
            self.stdout.write(f"{count} entrée(s) du journal d'audit seraient supprimées.")
            return
        queryset.delete()
        self.stdout.write(
            self.style.SUCCESS(f"{count} entrée(s) du journal d'audit supprimée(s).")
        )
