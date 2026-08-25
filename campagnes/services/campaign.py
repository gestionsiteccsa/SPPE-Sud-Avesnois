import logging
import secrets

from django.db import models, transaction
from django.db.models import Count, Q
from django.utils import timezone

from structures.audit import get_audit_actor
from structures.models import AuditLog, Structure

from ..emails import send_verification_invitation_email
from ..models import (
    ASSISTANTE_MATERNELLE_TYPE,
    UpdateCampaign,
    UpdateRequest,
    UpdateRequestField,
    VerificationInvitation,
)

logger = logging.getLogger(__name__)

# Champs modifiables depuis la page publique ; commune est une FK résolue par identifiant.
PUBLIC_FIELDS = (
    "telephone",
    "email",
    "adresse",
    "commune",
    "places_disponibles",
    "conditions_places",
)
FIELD_LABELS = {
    "telephone": "Téléphone",
    "email": "E-mail",
    "adresse": "Adresse",
    "commune": "Commune",
    "places_disponibles": "Places disponibles",
    "conditions_places": "Informations complémentaires",
}


class CampaignError(Exception):
    """Erreur métier liée au cycle de vie d'une campagne."""


def target_structures():
    """Population d'une campagne V1 : assistantes maternelles affichées sur le site."""
    return (
        Structure.objects.filter(
            type__nom=ASSISTANTE_MATERNELLE_TYPE,
            afficher=True,
        )
        .select_related("type", "commune")
        .order_by("commune__nom", "nom_structure", "nom", "prenom")
    )


def _channel_for(structure):
    return (
        VerificationInvitation.CHANNEL_EMAIL
        if structure.email
        else VerificationInvitation.CHANNEL_LETTER
    )


def _test_recipients(campaign: UpdateCampaign) -> list[str]:
    """Adresses de test configurées ; vide si aucune."""
    return [
        part.strip().lower()
        for part in campaign.test_emails.split(",")
        if part.strip()
    ]


def _send_email(invitation, raw_token, recipients) -> None:
    try:
        send_verification_invitation_email(invitation, raw_token, recipients)
        invitation.status = VerificationInvitation.STATUS_SENT
        invitation.sent_at = timezone.now()
    except Exception:
        logger.exception(
            "Échec d'envoi de l'invitation %s (campagne %s)",
            invitation.pk,
            invitation.campaign_id,
        )
        invitation.status = VerificationInvitation.STATUS_SEND_ERROR


def launch_campaign(campaign: UpdateCampaign):
    """Lance une campagne : invitations + jetons, envoi des e-mails, canal courrier sinon.

    En mode test, toutes les invitations (y compris celles prévues en courrier)
    sont envoyées aux adresses de test : aucun e-mail réel ne part.
    Les envois réseau ont lieu hors transaction : une campagne de grande taille
    ne maintient pas une transaction ouverte pendant toute la durée des envois.
    Les invitations sont créées en une seule opération groupée (l'audit consigne
    un résumé plutôt qu'une entrée par fiche).
    """
    if campaign.status != UpdateCampaign.STATUS_DRAFT:
        raise CampaignError("Seule une campagne en brouillon peut être lancée.")
    test_recipients = _test_recipients(campaign) if campaign.test_mode else []
    if campaign.test_mode and not test_recipients:
        raise CampaignError("Renseignez au moins une adresse e-mail de test.")
    today = timezone.localdate()
    if today < campaign.starts_at:
        raise CampaignError(
            "La campagne ne peut pas être lancée avant sa date de début "
            f"({campaign.starts_at.strftime('%d/%m/%Y')})."
        )
    if today > campaign.ends_at:
        raise CampaignError(
            "La campagne ne peut pas être lancée après sa date de fin "
            f"({campaign.ends_at.strftime('%d/%m/%Y')})."
        )
    targets = list(target_structures())
    expires_at = campaign.period_end
    invitations = []
    pending_sends = []
    for structure in targets:
        raw_token = secrets.token_urlsafe(32)
        channel = _channel_for(structure)
        if campaign.test_mode:
            status, recipients = (
                VerificationInvitation.STATUS_SEND_SCHEDULED,
                test_recipients,
            )
        elif channel == VerificationInvitation.CHANNEL_EMAIL:
            status, recipients = (
                VerificationInvitation.STATUS_SEND_SCHEDULED,
                [structure.email],
            )
        else:
            status, recipients = (
                VerificationInvitation.STATUS_NOT_CONTACTED,
                None,
            )
        invitation = VerificationInvitation(
            campaign=campaign,
            structure=structure,
            token_hash=VerificationInvitation.hash_token(raw_token),
            expires_at=expires_at,
            delivery_channel=channel,
            status=status,
        )
        invitations.append(invitation)
        if recipients is not None:
            pending_sends.append((invitation, raw_token, recipients))
    with transaction.atomic():
        VerificationInvitation.objects.bulk_create(invitations, batch_size=200)
        campaign.status = UpdateCampaign.STATUS_OPEN
        campaign.save(update_fields=["status"])
        if targets:
            AuditLog.objects.create(
                user=get_audit_actor(),
                action="batch",
                model_name="UpdateCampaign",
                object_id=campaign.pk,
                object_repr=f"Campagne « {campaign.name} » lancée",
                changes={"_invitations_created": len(targets)},
            )
    for invitation, raw_token, recipients in pending_sends:
        _send_email(invitation, raw_token, recipients)
    if pending_sends:
        VerificationInvitation.objects.bulk_update(
            [invitation for invitation, _raw, _recipients in pending_sends],
            ["status", "sent_at"],
            batch_size=200,
        )
    return len(targets)


def go_live(campaign: UpdateCampaign) -> int:
    """Passe une campagne testée en réel : nouveaux jetons, envoi aux vraies adresses."""
    if not campaign.test_mode:
        raise CampaignError("Cette campagne n'est pas en mode test.")
    if campaign.status != UpdateCampaign.STATUS_OPEN:
        raise CampaignError("Seule une campagne en cours peut passer en réel.")
    invitations = list(
        campaign.invitations.filter(
            status__in=VerificationInvitation.STATUS_UNANSWERED
        ).select_related("structure")
    )
    pending_sends = []
    for invitation in invitations:
        raw_token = VerificationInvitation.issue_new_token(invitation, campaign)
        if invitation.delivery_channel == VerificationInvitation.CHANNEL_EMAIL:
            invitation.status = VerificationInvitation.STATUS_SEND_SCHEDULED
            pending_sends.append(
                (invitation, raw_token, [invitation.structure.email])
            )
        else:
            invitation.status = VerificationInvitation.STATUS_NOT_CONTACTED
    with transaction.atomic():
        campaign.test_mode = False
        campaign.save(update_fields=["test_mode"])
        if invitations:
            VerificationInvitation.objects.bulk_update(
                invitations,
                ["token_hash", "expires_at", "status"],
                batch_size=200,
            )
            AuditLog.objects.create(
                user=get_audit_actor(),
                action="batch",
                model_name="UpdateCampaign",
                object_id=campaign.pk,
                object_repr=f"Campagne « {campaign.name} » passée en réel",
                changes={"_reissued": len(invitations), "_sent": len(pending_sends)},
            )
    for invitation, raw_token, recipients in pending_sends:
        _send_email(invitation, raw_token, recipients)
    if pending_sends:
        VerificationInvitation.objects.bulk_update(
            [invitation for invitation, _raw, _recipients in pending_sends],
            ["status", "sent_at"],
            batch_size=200,
        )
    return len(invitations)


def remind_unanswered(campaign: UpdateCampaign) -> int:
    """Relance les personnes n'ayant pas encore répondu (nouveau jeton à chaque envoi)."""
    if campaign.status != UpdateCampaign.STATUS_OPEN:
        raise CampaignError("Seule une campagne en cours peut être relancée.")
    test_recipients = _test_recipients(campaign) if campaign.test_mode else []
    invitations = list(
        campaign.invitations.filter(
            status__in=VerificationInvitation.STATUS_UNANSWERED
        ).select_related("structure")
    )
    pending_sends = []
    for invitation in invitations:
        raw_token = VerificationInvitation.issue_new_token(invitation, campaign)
        if campaign.test_mode:
            invitation.status = VerificationInvitation.STATUS_SEND_SCHEDULED
            pending_sends.append((invitation, raw_token, test_recipients))
        elif invitation.delivery_channel == VerificationInvitation.CHANNEL_EMAIL:
            invitation.status = VerificationInvitation.STATUS_SEND_SCHEDULED
            pending_sends.append((invitation, raw_token, [invitation.structure.email]))
        else:
            invitation.status = VerificationInvitation.STATUS_SEND_SCHEDULED
    with transaction.atomic():
        if invitations:
            VerificationInvitation.objects.bulk_update(
                invitations,
                ["token_hash", "expires_at", "status"],
                batch_size=200,
            )
            AuditLog.objects.create(
                user=get_audit_actor(),
                action="batch",
                model_name="UpdateCampaign",
                object_id=campaign.pk,
                object_repr=f"Relance de la campagne « {campaign.name} »",
                changes={"_reminded": len(invitations), "_sent": len(pending_sends)},
            )
    for invitation, raw_token, recipients in pending_sends:
        _send_email(invitation, raw_token, recipients)
    if pending_sends:
        VerificationInvitation.objects.bulk_update(
            [invitation for invitation, _raw, _recipients in pending_sends],
            ["status", "sent_at"],
            batch_size=200,
        )
    return len(invitations)


def generate_letters(campaign: UpdateCampaign) -> list[tuple[VerificationInvitation, str]]:
    """Prépare les courriers : jeton neuf par invitation courrier, rendu à l'impression."""
    if campaign.status != UpdateCampaign.STATUS_OPEN:
        raise CampaignError("Les courriers ne peuvent être générés que pour une campagne en cours.")
    invitations = list(
        campaign.invitations.filter(
            delivery_channel=VerificationInvitation.CHANNEL_LETTER,
            status__in=(
                VerificationInvitation.STATUS_NOT_CONTACTED,
                VerificationInvitation.STATUS_SEND_SCHEDULED,
            ),
        ).select_related("structure")
    )
    batch = []
    for invitation in invitations:
        raw_token = VerificationInvitation.issue_new_token(invitation, campaign)
        invitation.status = VerificationInvitation.STATUS_SEND_SCHEDULED
        batch.append((invitation, raw_token))
    if invitations:
        with transaction.atomic():
            VerificationInvitation.objects.bulk_update(
                invitations,
                ["token_hash", "expires_at", "status"],
                batch_size=200,
            )
            AuditLog.objects.create(
                user=get_audit_actor(),
                action="batch",
                model_name="UpdateCampaign",
                object_id=campaign.pk,
                object_repr=f"Courriers générés pour « {campaign.name} »",
                changes={"_letters": len(invitations)},
            )
    return batch


def close_campaign(campaign: UpdateCampaign) -> int:
    """Clôture : les sans-réponse passent en « expiré », la campagne est clôturée."""
    if campaign.status == UpdateCampaign.STATUS_CLOSED:
        raise CampaignError("Cette campagne est déjà clôturée.")
    with transaction.atomic():
        expired = campaign.invitations.filter(
            status__in=VerificationInvitation.STATUS_UNANSWERED
        ).update(status=VerificationInvitation.STATUS_EXPIRED)
        campaign.status = UpdateCampaign.STATUS_CLOSED
        campaign.closed_at = timezone.now()
        campaign.save(update_fields=["status", "closed_at"])
    return expired


def _stringify(structure, field_name: str) -> str:
    field = Structure._meta.get_field(field_name)
    if field_name == "commune" or isinstance(field, models.ForeignKey):
        value_id = getattr(structure, f"{field_name}_id", None)
        return str(value_id) if value_id is not None else ""
    value = getattr(structure, field_name)
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _build_changes(structure, changes: dict[str, str]) -> list[tuple[str, str, str]]:
    """Filtre les champs modifiés : (field_name, old_value, new_value).

    Une valeur vide signifie « inchangé » : aucune proposition de suppression
    n'est possible depuis la page publique.
    """
    rows = []
    for field_name in PUBLIC_FIELDS:
        if field_name not in changes:
            continue
        new_value = (changes[field_name] or "").strip()
        if not new_value:
            continue
        old_value = _stringify(structure, field_name)
        if field_name == "commune" and new_value:
            new_value = str(int(new_value))
        if new_value != old_value:
            rows.append((field_name, old_value, new_value))
    return rows


def _check_no_pending_request(invitation: VerificationInvitation) -> None:
    pending = invitation.requests.filter(status=UpdateRequest.STATUS_PENDING).exclude(
        request_type=UpdateRequest.REQUEST_CONFIRMATION
    )
    if pending.exists():
        raise CampaignError("Une demande est déjà en attente de validation pour cette fiche.")


def submit_confirmation(invitation: VerificationInvitation, channel: str) -> UpdateRequest:
    """La personne confirme que ses informations sont correctes."""
    _check_no_pending_request(invitation)
    with transaction.atomic():
        request = UpdateRequest.objects.create(
            invitation=invitation,
            request_type=UpdateRequest.REQUEST_CONFIRMATION,
            channel=channel,
        )
        invitation.status = VerificationInvitation.STATUS_CONFIRMED
        invitation.completed_at = timezone.now()
        invitation.save(update_fields=["status", "completed_at"])
    return request


def submit_stop_activity(invitation: VerificationInvitation, channel: str) -> UpdateRequest:
    _check_no_pending_request(invitation)
    with transaction.atomic():
        request = UpdateRequest.objects.create(
            invitation=invitation,
            request_type=UpdateRequest.REQUEST_STOP_ACTIVITY,
            channel=channel,
        )
        invitation.status = VerificationInvitation.STATUS_PENDING_REVIEW
        invitation.completed_at = timezone.now()
        invitation.save(update_fields=["status", "completed_at"])
    return request


def submit_wrong_fiche(invitation: VerificationInvitation, channel: str) -> UpdateRequest:
    _check_no_pending_request(invitation)
    with transaction.atomic():
        request = UpdateRequest.objects.create(
            invitation=invitation,
            request_type=UpdateRequest.REQUEST_WRONG_FICHE,
            channel=channel,
        )
        invitation.status = VerificationInvitation.STATUS_PENDING_REVIEW
        invitation.completed_at = timezone.now()
        invitation.save(update_fields=["status", "completed_at"])
    return request


def submit_modification(
    invitation: VerificationInvitation,
    channel: str,
    changes: dict[str, str],
) -> UpdateRequest:
    """Enregistre une proposition de modification sans jamais toucher la fiche officielle."""
    rows = _build_changes(invitation.structure, changes)
    if not rows:
        raise CampaignError("Aucune modification proposée.")
    _check_no_pending_request(invitation)
    with transaction.atomic():
        request = UpdateRequest.objects.create(
            invitation=invitation,
            request_type=UpdateRequest.REQUEST_MODIFICATION,
            channel=channel,
        )
        fields = UpdateRequestField.objects.bulk_create(
            [
                UpdateRequestField(
                    request=request,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                )
                for field_name, old_value, new_value in rows
            ]
        )
        invitation.status = VerificationInvitation.STATUS_PENDING_REVIEW
        invitation.completed_at = timezone.now()
        invitation.save(update_fields=["status", "completed_at"])
    AuditLog.objects.create(
        user=get_audit_actor(),
        action="create",
        model_name="UpdateRequestField",
        object_id=request.pk,
        object_repr=f"{len(fields)} champ(s) proposé(s) — {invitation.structure}",
        changes={
            "fields": [
                {
                    "field_name": field.field_name,
                    "old_value": field.old_value,
                    "new_value": field.new_value,
                }
                for field in fields
            ]
        },
    )
    return request


def create_assisted_request(
    invitation: VerificationInvitation,
    request_type: str,
    changes: dict[str, str],
    channel: str,
    agent,
) -> UpdateRequest:
    """Saisie par un agent (téléphone ou accueil) au nom de la personne concernée."""
    if request_type == UpdateRequest.REQUEST_MODIFICATION:
        request = submit_modification(invitation, channel, changes)
    elif request_type == UpdateRequest.REQUEST_CONFIRMATION:
        request = submit_confirmation(invitation, channel)
    elif request_type == UpdateRequest.REQUEST_STOP_ACTIVITY:
        request = submit_stop_activity(invitation, channel)
    elif request_type == UpdateRequest.REQUEST_WRONG_FICHE:
        request = submit_wrong_fiche(invitation, channel)
    else:
        raise CampaignError("Type de demande inconnu.")
    request.created_by = agent
    request.save(update_fields=["created_by"])
    return request


def _coerce_new_value(field_name: str, raw: str):
    field = Structure._meta.get_field(field_name)
    if field_name == "commune" or isinstance(field, models.ForeignKey):
        return int(raw) if raw else None
    if isinstance(field, models.IntegerField):
        return int(raw) if raw else None
    if isinstance(field, models.BooleanField):
        return raw == "true"
    return raw


def _apply_accepted_field(structure: Structure, field_name: str, raw: str) -> None:
    value = _coerce_new_value(field_name, raw)
    if field_name == "commune":
        structure.commune_id = value
    else:
        setattr(structure, field_name, value)


def review_request(
    request: UpdateRequest,
    decision: str,
    accepted_field_ids: list[int],
    comment: str,
    reviewer,
) -> None:
    """Valide ou refuse une demande ; les champs acceptés sont copiés sur la fiche officielle."""
    if request.status != UpdateRequest.STATUS_PENDING:
        raise CampaignError("Cette demande a déjà été traitée.")
    fields = list(request.fields.all())
    if decision == "accept_all":
        accepted = fields
    elif decision == "accept_selected":
        accepted = [f for f in fields if f.pk in accepted_field_ids]
    else:
        accepted = []
    accepted = [f for f in accepted if f.new_value != f.old_value]
    rejected = [f for f in fields if f not in accepted]

    with transaction.atomic():
        request.reviewed_by = reviewer
        request.reviewed_at = timezone.now()
        request.review_comment = comment.strip()
        request.status = (
            UpdateRequest.STATUS_ACCEPTED if accepted else UpdateRequest.STATUS_REJECTED
        )
        request.save(
            update_fields=["reviewed_by", "reviewed_at", "review_comment", "status"]
        )
        UpdateRequestField.objects.filter(pk__in=[f.pk for f in accepted]).update(
            decision=UpdateRequestField.DECISION_ACCEPTED
        )
        UpdateRequestField.objects.filter(pk__in=[f.pk for f in rejected]).update(
            decision=UpdateRequestField.DECISION_REJECTED
        )

        invitation = request.invitation
        invitation.status = (
            VerificationInvitation.STATUS_VALIDATED
            if accepted
            else VerificationInvitation.STATUS_REJECTED
        )
        invitation.save(update_fields=["status"])

        if request.request_type == UpdateRequest.REQUEST_MODIFICATION and accepted:
            structure = invitation.structure
            for field in accepted:
                _apply_accepted_field(structure, field.field_name, field.new_value)
            structure.save()

        AuditLog.objects.create(
            user=reviewer,
            action="update",
            model_name="UpdateRequest",
            object_id=request.pk,
            object_repr=f"{request.get_request_type_display()} — {invitation.structure}",
            changes={
                "decision": decision,
                "accepted_fields": [f.field_name for f in accepted],
                "comment": request.review_comment,
            },
        )


def campaign_stats(campaign: UpdateCampaign) -> dict:
    """Indicateurs du tableau de bord d'une campagne."""
    invitations = campaign.invitations
    base = invitations.aggregate(
        total=Count("id"),
        sent=Count("id", filter=Q(status=VerificationInvitation.STATUS_SENT)),
        send_error=Count("id", filter=Q(status=VerificationInvitation.STATUS_SEND_ERROR)),
        without_email=Count("id", filter=Q(delivery_channel=VerificationInvitation.CHANNEL_LETTER)),
        consulted=Count("id", filter=Q(status=VerificationInvitation.STATUS_OPENED)),
        confirmed=Count("id", filter=Q(status=VerificationInvitation.STATUS_CONFIRMED)),
        pending_review=Count(
            "id", filter=Q(status=VerificationInvitation.STATUS_PENDING_REVIEW)
        ),
        validated=Count("id", filter=Q(status=VerificationInvitation.STATUS_VALIDATED)),
        rejected=Count("id", filter=Q(status=VerificationInvitation.STATUS_REJECTED)),
        expired=Count("id", filter=Q(status=VerificationInvitation.STATUS_EXPIRED)),
        unanswered=Count("id", filter=Q(status__in=VerificationInvitation.STATUS_UNANSWERED)),
    )
    requests = invitations.aggregate(
        requests_total=Count("requests"),
        requests_pending=Count(
            "requests",
            filter=Q(requests__status=UpdateRequest.STATUS_PENDING)
            & ~Q(requests__request_type=UpdateRequest.REQUEST_CONFIRMATION),
        ),
        requests_accepted=Count(
            "requests", filter=Q(requests__status=UpdateRequest.STATUS_ACCEPTED)
        ),
        requests_rejected=Count(
            "requests", filter=Q(requests__status=UpdateRequest.STATUS_REJECTED)
        ),
    )
    base.update(requests)
    responded = (
        base["confirmed"]
        + base["pending_review"]
        + base["validated"]
        + base["rejected"]
    )
    base["responded"] = responded
    base["response_rate"] = round(responded * 100 / base["total"], 1) if base["total"] else 0.0
    return base