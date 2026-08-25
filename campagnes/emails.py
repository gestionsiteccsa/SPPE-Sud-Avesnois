from django.conf import settings
from django.core.mail import EmailMessage

from .models import VerificationInvitation


def _send(subject: str, message: str, recipients: list[str]) -> None:
    EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    ).send()


def _verification_link(raw_token: str) -> str:
    return f"{settings.SITE_URL}/verification/{raw_token}/"


def build_invitation_email(
    invitation: VerificationInvitation, raw_token: str, test_mode: bool = False
) -> tuple[str, str]:
    """Construit l'objet et le corps du message de vérification (texte simple)."""
    campaign = invitation.campaign
    structure = invitation.structure
    subject = "Vérification annuelle de vos informations — SPPE Sud-Avesnois"
    if test_mode:
        subject = f"[TEST] {subject}"
    lines = [
        f"Bonjour {structure.nom_affiche},",
        "",
        "Dans le cadre de la mise à jour annuelle de l'annuaire des structures "
        "petite enfance, merci de vérifier les informations vous concernant.",
        "",
        f"Cette vérification est disponible jusqu'au "
        f"{campaign.ends_at.strftime('%d/%m/%Y')}.",
        "",
        "Aucun compte n'est nécessaire : il vous suffit d'ouvrir votre lien personnel :",
        "",
        _verification_link(raw_token),
        "",
        "Important : ce lien est personnel. Ne le transmettez à personne.",
    ]
    if campaign.message.strip():
        lines += ["", "—", "", campaign.message.strip()]
    lines += [
        "",
        "En cas de difficulté, vous pouvez nous contacter à cette adresse :",
        settings.DEFAULT_FROM_EMAIL,
        "",
        "Cordialement,",
        "SPPE Sud-Avesnois",
    ]
    return subject, "\n".join(lines)


def send_verification_invitation_email(
    invitation: VerificationInvitation, raw_token: str, recipients: list[str] | None = None
) -> None:
    """Envoie le lien personnel ; lève une exception en cas d'échec d'envoi.

    En mode test, les destinataires sont passés explicitement : aucune adresse
    réelle n'est jamais utilisée.
    """
    subject, body = build_invitation_email(
        invitation, raw_token, test_mode=invitation.campaign.test_mode
    )
    _send(subject, body, recipients or [invitation.structure.email])