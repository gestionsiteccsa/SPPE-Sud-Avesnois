import hashlib
import secrets
from datetime import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from structures.models import Structure

ASSISTANTE_MATERNELLE_TYPE = "Assistante maternelle"


def _period_end(day):
    """Fin de journée d'une campagne, pour borner la validité d'un jeton."""
    return timezone.make_aware(
        timezone.datetime.combine(day, time(23, 59, 59)),
        timezone.get_current_timezone(),
    )


def _period_start(day):
    """Début de journée d'une campagne."""
    return timezone.make_aware(
        timezone.datetime.combine(day, time(0, 0, 0)),
        timezone.get_current_timezone(),
    )


class UpdateCampaign(models.Model):
    STATUS_DRAFT = "brouillon"
    STATUS_OPEN = "en_cours"
    STATUS_CLOSED = "cloturee"
    STATUS_ARCHIVED = "archivee"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Brouillon"),
        (STATUS_OPEN, "En cours"),
        (STATUS_CLOSED, "Clôturée"),
        (STATUS_ARCHIVED, "Archivée"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nom")
    starts_at = models.DateField(verbose_name="Date de début")
    ends_at = models.DateField(verbose_name="Date de fin")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name="Statut",
    )
    message = models.TextField(blank=True, verbose_name="Message d'introduction")
    test_mode = models.BooleanField(
        default=False,
        verbose_name="Mode test",
        help_text="Les e-mails sont envoyés uniquement aux adresses de test, jamais aux personnes.",
    )
    test_emails = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Adresses e-mail de test",
        help_text="2-3 adresses séparées par des virgules, utilisées uniquement en mode test.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de clôture")

    class Meta:
        verbose_name = "Campagne de mise à jour"
        verbose_name_plural = "Campagnes de mise à jour"
        ordering = ["-starts_at", "-created_at"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.ends_at and self.starts_at and self.ends_at < self.starts_at:
            raise ValidationError(
                {"ends_at": "La date de fin doit être postérieure ou égale à la date de début."}
            )

    @property
    def period_start(self):
        return _period_start(self.starts_at)

    @property
    def period_end(self):
        return _period_end(self.ends_at)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance


class VerificationInvitation(models.Model):
    STATUS_NOT_CONTACTED = "non_contacte"
    STATUS_SEND_SCHEDULED = "envoi_programme"
    STATUS_SENT = "envoye"
    STATUS_SEND_ERROR = "erreur_envoi"
    STATUS_OPENED = "consulte"
    STATUS_CONFIRMED = "confirme_sans_modification"
    STATUS_PENDING_REVIEW = "en_attente_validation"
    STATUS_VALIDATED = "valide"
    STATUS_REJECTED = "refuse"
    STATUS_EXPIRED = "expire"
    STATUS_CHOICES = [
        (STATUS_NOT_CONTACTED, "Non contacté"),
        (STATUS_SEND_SCHEDULED, "Envoi programmé"),
        (STATUS_SENT, "Envoyé"),
        (STATUS_SEND_ERROR, "Erreur d'envoi"),
        (STATUS_OPENED, "Consulté"),
        (STATUS_CONFIRMED, "Confirmé sans modification"),
        (STATUS_PENDING_REVIEW, "En attente de validation"),
        (STATUS_VALIDATED, "Validé"),
        (STATUS_REJECTED, "Refusé"),
        (STATUS_EXPIRED, "Expiré"),
    ]
    STATUS_RESPONDED = {
        STATUS_CONFIRMED,
        STATUS_PENDING_REVIEW,
        STATUS_VALIDATED,
        STATUS_REJECTED,
    }
    STATUS_UNANSWERED = {
        STATUS_NOT_CONTACTED,
        STATUS_SEND_SCHEDULED,
        STATUS_SENT,
        STATUS_SEND_ERROR,
        STATUS_OPENED,
    }

    CHANNEL_EMAIL = "email"
    CHANNEL_LETTER = "courrier"
    CHANNEL_PHONE = "telephone"
    CHANNEL_RECEPTION = "accueil"
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "E-mail"),
        (CHANNEL_LETTER, "Courrier"),
        (CHANNEL_PHONE, "Téléphone"),
        (CHANNEL_RECEPTION, "Accueil physique"),
    ]

    campaign = models.ForeignKey(
        UpdateCampaign,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="Campagne",
    )
    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Fiche",
    )
    token_hash = models.CharField(
        max_length=64,
        blank=True,
        unique=True,
        verbose_name="Empreinte du jeton",
    )
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expiration du jeton")
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_CONTACTED,
        verbose_name="Statut",
    )
    delivery_channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        blank=True,
        verbose_name="Canal prévu",
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyé le")
    opened_at = models.DateTimeField(null=True, blank=True, verbose_name="Première consultation")
    opened_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'ouvertures")
    last_opened_at = models.DateTimeField(null=True, blank=True, verbose_name="Dernière consultation")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Répondu le")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Invitation à vérifier"
        verbose_name_plural = "Invitations à vérifier"
        ordering = ["structure__nom_structure", "structure__nom", "structure__prenom"]
        constraints = [
            models.UniqueConstraint(
                fields=["campaign", "structure"],
                name="campagnes_invitation_unique_campagne_fiche",
            ),
        ]

    def __str__(self):
        return f"{self.structure} — {self.campaign}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @classmethod
    def find_by_token(cls, raw_token: str):
        return (
            cls.objects.select_related("campaign", "structure__type", "structure__commune")
            .filter(token_hash=cls.hash_token(raw_token))
            .first()
        )

    @classmethod
    def create_with_token(cls, campaign, structure):
        """Crée une invitation avec un jeton aléatoire ; seule son empreinte est stockée."""
        raw_token = secrets.token_urlsafe(32)
        invitation = cls.objects.create(
            campaign=campaign,
            structure=structure,
            token_hash=cls.hash_token(raw_token),
            expires_at=campaign.period_end,
        )
        return invitation, raw_token

    @classmethod
    def issue_new_token(cls, invitation, campaign: "UpdateCampaign | None" = None):
        """Remplace le jeton d'une invitation (relance, erreur d'envoi, courrier imprimé).

        La campagne peut être passée explicitement pour éviter une requête par
        invitation dans les traitements groupés.
        """
        if campaign is None:
            campaign = invitation.campaign
        raw_token = secrets.token_urlsafe(32)
        invitation.token_hash = cls.hash_token(raw_token)
        invitation.expires_at = campaign.period_end
        return raw_token

    @property
    def has_responded(self) -> bool:
        return self.status in self.STATUS_RESPONDED

    @property
    def is_valid_token(self) -> bool:
        """Jeton reconnu, dans la période de la campagne (lecture possible)."""
        campaign = self.campaign
        if campaign.status != UpdateCampaign.STATUS_OPEN:
            return False
        now = timezone.now()
        return campaign.period_start <= now <= campaign.period_end

    @property
    def is_usable(self) -> bool:
        """Jeton encore utilisable pour soumettre une réponse."""
        return self.is_valid_token and not self.has_responded


class UpdateRequest(models.Model):
    REQUEST_CONFIRMATION = "confirmation"
    REQUEST_MODIFICATION = "modification"
    REQUEST_STOP_ACTIVITY = "arret_activite"
    REQUEST_WRONG_FICHE = "fiche_incorrecte"
    REQUEST_CHOICES = [
        (REQUEST_CONFIRMATION, "Confirmation sans modification"),
        (REQUEST_MODIFICATION, "Proposition de modification"),
        (REQUEST_STOP_ACTIVITY, "N'exerce plus cette activité"),
        (REQUEST_WRONG_FICHE, "Cette fiche ne me concerne pas"),
    ]

    STATUS_PENDING = "en_attente"
    STATUS_ACCEPTED = "acceptee"
    STATUS_REJECTED = "refusee"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_ACCEPTED, "Acceptée"),
        (STATUS_REJECTED, "Refusée"),
    ]

    invitation = models.ForeignKey(
        VerificationInvitation,
        on_delete=models.CASCADE,
        related_name="requests",
        verbose_name="Invitation",
    )
    request_type = models.CharField(
        max_length=30,
        choices=REQUEST_CHOICES,
        verbose_name="Type de demande",
    )
    channel = models.CharField(
        max_length=20,
        choices=VerificationInvitation.CHANNEL_CHOICES,
        verbose_name="Canal",
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Statut",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Validé par",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de décision")
    review_comment = models.TextField(blank=True, verbose_name="Commentaire interne")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Saisi par un agent",
        help_text="Renseigné lorsque la demande est saisie au nom de la personne.",
    )

    class Meta:
        verbose_name = "Demande de mise à jour"
        verbose_name_plural = "Demandes de mise à jour"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.get_request_type_display()} — {self.invitation.structure}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance


class UpdateRequestField(models.Model):
    DECISION_PENDING = "en_attente"
    DECISION_ACCEPTED = "acceptee"
    DECISION_REJECTED = "refusee"
    DECISION_CHOICES = [
        (DECISION_PENDING, "En attente"),
        (DECISION_ACCEPTED, "Acceptée"),
        (DECISION_REJECTED, "Refusée"),
    ]

    request = models.ForeignKey(
        UpdateRequest,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name="Demande",
    )
    field_name = models.CharField(max_length=100, verbose_name="Champ")
    old_value = models.TextField(blank=True, verbose_name="Valeur actuelle")
    new_value = models.TextField(blank=True, verbose_name="Valeur proposée")
    decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        default=DECISION_PENDING,
        verbose_name="Décision",
    )

    class Meta:
        verbose_name = "Champ proposé"
        verbose_name_plural = "Champs proposés"
        ordering = ["pk"]

    def __str__(self):
        return f"{self.field_name}: {self.old_value} → {self.new_value}"

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._audit_original = {
            f.name: f.value_from_object(instance) for f in cls._meta.fields
        }
        return instance