from django.contrib import admin
from django.contrib.admin.decorators import register

from app.admin_site import admin_site
from .models import UpdateCampaign, UpdateRequest, UpdateRequestField, VerificationInvitation


@register(UpdateCampaign, site=admin_site)
class UpdateCampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "starts_at", "ends_at", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "closed_at"]


@register(VerificationInvitation, site=admin_site)
class VerificationInvitationAdmin(admin.ModelAdmin):
    list_display = ["campaign", "structure", "status", "delivery_channel", "sent_at", "completed_at"]
    list_filter = ["status", "delivery_channel", "campaign"]
    search_fields = ["structure__nom", "structure__prenom", "structure__nom_structure"]
    autocomplete_fields = ["campaign", "structure"]
    readonly_fields = ["token_hash", "created_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("campaign", "structure")


@register(UpdateRequest, site=admin_site)
class UpdateRequestAdmin(admin.ModelAdmin):
    list_display = ["invitation", "request_type", "channel", "status", "submitted_at", "reviewed_by"]
    list_filter = ["request_type", "status", "channel"]
    readonly_fields = ["submitted_at", "reviewed_at"]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "invitation__campaign",
                "invitation__structure",
                "reviewed_by",
            )
        )


@register(UpdateRequestField, site=admin_site)
class UpdateRequestFieldAdmin(admin.ModelAdmin):
    list_display = ["request", "field_name", "old_value", "new_value", "decision"]
    list_filter = ["decision", "field_name"]
    readonly_fields = ["request"]