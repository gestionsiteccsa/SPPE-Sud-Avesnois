from django.conf import settings
from django.db import models


class FeedbackReport(models.Model):
    """Signalement envoyé depuis le bouton fixe du site."""

    TYPE_BUG = "bug"
    TYPE_SUGGESTION = "suggestion"
    TYPE_AUTRE = "autre"
    TYPE_CHOICES = [
        (TYPE_BUG, "Bug"),
        (TYPE_SUGGESTION, "Suggestion"),
        (TYPE_AUTRE, "Autre remarque"),
    ]

    STATUT_NOUVEAU = "nouveau"
    STATUT_EN_COURS = "en_cours"
    STATUT_RESOLU = "resolu"
    STATUT_CHOICES = [
        (STATUT_NOUVEAU, "Nouveau"),
        (STATUT_EN_COURS, "En cours"),
        (STATUT_RESOLU, "Résolu"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="feedback_reports",
        verbose_name="Utilisateur",
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_BUG,
        verbose_name="Type",
    )
    message = models.TextField(verbose_name="Message")
    page_auto = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Page détectée",
        help_text="Chemin déduit côté serveur (Referer), non modifiable.",
    )
    page_declaree = models.CharField(
        max_length=500,
        verbose_name="Page concernée",
        help_text="Page indiquée par l'utilisateur (pré-remplie, modifiable).",
    )
    url_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nom d'URL",
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Navigateur",
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default=STATUT_NOUVEAU,
        verbose_name="Statut",
    )
    commentaire_interne = models.TextField(
        blank=True,
        verbose_name="Commentaire interne",
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Traité par",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["statut", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} — {self.page_declaree or self.page_auto}"
