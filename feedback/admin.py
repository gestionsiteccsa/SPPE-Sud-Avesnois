from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register

from app.admin_site import admin_site
from .models import FeedbackReport


@register(FeedbackReport, site=admin_site)
class FeedbackReportAdmin(ModelAdmin):
    list_display = ("created_at", "type", "statut", "page_declaree", "auteur")
    list_filter = ("statut", "type", "created_at")
    search_fields = ("message", "page_declaree", "page_auto", "user__email")
    readonly_fields = (
        "user",
        "page_auto",
        "url_name",
        "user_agent",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (None, {"fields": ("type", "statut", "message", "page_declaree")}),
        (
            "Contexte détecté",
            {"fields": ("page_auto", "url_name", "user", "user_agent")},
        ),
        (
            "Suivi",
            {"fields": ("traite_par", "commentaire_interne")},
        ),
        (
            "Dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )
    actions = ["marquer_resolu", "marquer_en_cours"]

    @staticmethod
    def auteur(obj):
        return obj.user.email if obj.user else "—"

    def save_model(self, request, obj, form, change):
        if change and obj.statut != FeedbackReport.STATUT_NOUVEAU and not obj.traite_par:
            obj.traite_par = request.user
        super().save_model(request, obj, form, change)

    def marquer_resolu(self, request, queryset):
        queryset.update(statut=FeedbackReport.STATUT_RESOLU)

    marquer_resolu.short_description = "Marquer comme résolu"

    def marquer_en_cours(self, request, queryset):
        queryset.update(statut=FeedbackReport.STATUT_EN_COURS)

    marquer_en_cours.short_description = "Marquer en cours"
