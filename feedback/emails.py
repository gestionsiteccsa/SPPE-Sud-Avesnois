from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from authentication.models import DestinataireNotification

User = get_user_model()


def _fallback_admin_emails() -> list[str]:
    return list(
        User.objects.filter(is_superuser=True, is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )


def notify_admins_new_feedback(report, detail_url: str = "") -> None:
    """Prévient les gestionnaires d'un nouveau signalement (texte simple)."""
    actives = DestinataireNotification.objects.filter(actif=True)
    recipients = [dest.email for dest in actives if not dest.en_cci]
    cc = [dest.email for dest in actives if dest.en_cci]
    if not recipients and not cc:
        recipients = _fallback_admin_emails()
    if not recipients:
        return
    author = report.user.email if report.user and report.user.email else "inconnu"
    text_lines = [
        "Un nouveau signalement a été envoyé depuis le site.",
        "",
        f"Type : {report.get_type_display()}",
        f"Auteur : {author}",
        f"Page indiquée : {report.page_declaree}",
        f"Page détectée : {report.page_auto or '—'}",
        "",
        "Message :",
        report.message,
    ]
    if detail_url:
        text_lines += ["", f"Voir dans l'admin : {detail_url}"]
    html_body = render_to_string(
        "feedback/emails/nouveau_signalement.html",
        {"report": report, "author": author, "detail_url": detail_url},
    )
    message = EmailMultiAlternatives(
        subject="Nouveau signalement — SPPE Sud-Avesnois",
        body="\n".join(text_lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        cc=cc,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
