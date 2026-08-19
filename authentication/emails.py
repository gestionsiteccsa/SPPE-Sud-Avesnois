from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage

from .models import CollaborateurInscription, DestinataireNotification

User = get_user_model()


def _send(subject: str, message: str, recipients: list[str], *, cc: list[str] | None = None) -> None:
    EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        cc=cc or [],
    ).send()


def _fallback_admin_emails() -> list[str]:
    return list(
        User.objects.filter(is_superuser=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


def notify_admins_new_inscription(inscription: CollaborateurInscription, dashboard_url: str) -> None:
    actives = DestinataireNotification.objects.filter(actif=True)
    recipients = [
        dest.email for dest in actives if not dest.en_cci
    ]
    cc = [dest.email for dest in actives if dest.en_cci]
    if not recipients and not cc:
        recipients = _fallback_admin_emails()
    if not recipients:
        return
    _send(
        subject="Nouvelle demande d'inscription — SPPE Sud-Avesnois",
        message=(
            f"Un collaborateur a demandé son inscription.\n\n"
            f"Nom : {inscription.user.last_name}\n"
            f"Prénom : {inscription.user.first_name}\n"
            f"Email : {inscription.user.email}\n\n"
            f"Pour valider ou refuser la demande : {dashboard_url}"
        ),
        recipients=recipients,
        cc=cc,
    )


def notify_collaborateur_validee(user) -> None:
    _send(
        subject="Votre inscription a été validée — SPPE Sud-Avesnois",
        message=(
            f"Bonjour {user.first_name},\n\n"
            f"Votre demande d'inscription a été validée. Vous pouvez dès maintenant "
            f"vous connecter pour gérer les structures de vos communes.\n\n"
            f"{settings.SITE_URL}"
        ),
        recipients=[user.email],
    )


def notify_collaborateur_refusee(user) -> None:
    _send(
        subject="Votre demande d'inscription — SPPE Sud-Avesnois",
        message=(
            f"Bonjour {user.first_name},\n\n"
            f"Votre demande d'inscription n'a pas été retenue pour le moment. "
            f"Vous pouvez recontacter l'administrateur du site pour plus d'informations."
        ),
        recipients=[user.email],
    )
