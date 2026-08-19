from django.conf import settings
from django.db import models


class CollaborateurInscription(models.Model):
    STATUT_EN_ATTENTE = "en_attente"
    STATUT_VALIDEE = "validee"
    STATUT_REFUSEE = "refusee"
    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, "En attente de validation"),
        (STATUT_VALIDEE, "Validée"),
        (STATUT_REFUSEE, "Refusée"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default=STATUT_EN_ATTENTE,
        verbose_name="Statut",
    )
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date de la demande")
    date_decision = models.DateTimeField(null=True, blank=True, verbose_name="Date de décision")
    decideur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Décideur",
    )

    class Meta:
        verbose_name = "Demande d'inscription"
        verbose_name_plural = "Demandes d'inscription"
        ordering = ["-date_demande"]

    def __str__(self):
        return f"{self.user.email} — {self.get_statut_display()}"


class DestinataireNotification(models.Model):
    """Adresse recevant les notifications de demandes d'inscription."""

    email = models.EmailField(unique=True, verbose_name="Adresse email")
    actif = models.BooleanField(
        default=True,
        verbose_name="Recevoir les notifications",
    )
    en_cci = models.BooleanField(
        default=False,
        verbose_name="En copie cachée (CCI)",
        help_text="L'adresse est placée en copie cachée au lieu des destinataires principaux.",
    )

    class Meta:
        verbose_name = "Destinataire de notification"
        verbose_name_plural = "Destinataires de notifications"
        ordering = ["email"]

    def __str__(self):
        return self.email


class UserCommune(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
    )
    commune = models.ForeignKey(
        "communes.Commune",
        on_delete=models.CASCADE,
        verbose_name="Commune",
    )

    class Meta:
        verbose_name = "Commune liée"
        verbose_name_plural = "Communes liées"
        unique_together = [("user", "commune")]

    def __str__(self):
        return f"{self.user.email} — {self.commune}"
