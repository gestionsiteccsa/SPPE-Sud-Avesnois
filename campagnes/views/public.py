from django.conf import settings
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit

from ..forms import VerificationModificationForm
from ..models import VerificationInvitation
from ..services.campaign import (
    FIELD_LABELS,
    CampaignError,
    submit_confirmation,
    submit_modification,
    submit_stop_activity,
    submit_wrong_fiche,
)


class VerificationView(View):
    """Page publique de vérification : accès uniquement par jeton personnel."""

    def _record_opening(self, invitation) -> None:
        """Incrémente le compteur d'ouvertures sans lecture-écriture concurrente.

        La mise à jour directe en base évite les pertes d'incréments si la page
        est ouverte plusieurs fois simultanément ; elle ne déclenche pas les
        signaux d'audit (traçage analytique, pas une modification métier).
        """
        now = timezone.now()
        updates = {
            "opened_count": F("opened_count") + 1,
            "last_opened_at": now,
        }
        if invitation.opened_at is None:
            updates["opened_at"] = now
        if invitation.status in VerificationInvitation.STATUS_UNANSWERED:
            updates["status"] = VerificationInvitation.STATUS_OPENED
        VerificationInvitation.objects.filter(pk=invitation.pk).update(**updates)
        invitation.opened_count += 1

    def _render_form(self, request, invitation, form=None, token=""):
        structure = invitation.structure
        if form is None:
            form = VerificationModificationForm(
                initial={
                    "telephone": structure.telephone,
                    "email": structure.email,
                    "adresse": structure.adresse,
                    "commune": structure.commune_id,
                    "places_disponibles": structure.places_disponibles,
                    "conditions_places": structure.conditions_places,
                }
            )
        return render(
            request,
            "campagnes/verification_form.html",
            {
                "invitation": invitation,
                "structure": structure,
                "form": form,
                "labels": FIELD_LABELS,
                "token": token,
            },
        )

    def _render_submitted(self, request, invitation):
        latest = invitation.requests.order_by("-submitted_at").first()
        return render(
            request,
            "campagnes/verification_submitted.html",
            {
                "invitation": invitation,
                "latest_request": latest,
                "field_labels": FIELD_LABELS,
            },
        )

    def _invalid(self, request):
        return render(
            request,
            "campagnes/verification_invalid.html",
            {"contact_email": settings.DEFAULT_FROM_EMAIL},
            status=404,
        )

    def get(self, request: HttpRequest, token: str) -> HttpResponse:
        invitation = VerificationInvitation.find_by_token(token)
        if invitation is None or not invitation.is_valid_token:
            return self._invalid(request)
        if invitation.has_responded:
            return self._render_submitted(request, invitation)
        self._record_opening(invitation)
        return self._render_form(request, invitation, token=token)

    @method_decorator(ratelimit(key="ip", rate="20/h", method="POST", block=True))
    def post(self, request: HttpRequest, token: str) -> HttpResponse:
        invitation = VerificationInvitation.find_by_token(token)
        if invitation is None or not invitation.is_usable or invitation.has_responded:
            return self._invalid(request)

        channel = invitation.delivery_channel or VerificationInvitation.CHANNEL_LETTER
        action = request.POST.get("action", "")
        if action == "confirmer":
            try:
                submit_confirmation(invitation, channel)
            except CampaignError as error:
                return self._render_form(
                    request, invitation, self._form_with_error(request, error), token
                )
            return self._render_submitted(request, invitation)
        if action == "modifier":
            form = VerificationModificationForm(request.POST)
            if not form.is_valid():
                return self._render_form(request, invitation, form, token)
            try:
                submit_modification(invitation, channel, form.changes())
            except CampaignError as error:
                form = self._form_with_error(request, error)
                return self._render_form(request, invitation, form, token)
            return self._render_submitted(request, invitation)
        if action == "arreter":
            try:
                submit_stop_activity(invitation, channel)
            except CampaignError as error:
                return self._render_form(
                    request, invitation, self._form_with_error(request, error), token
                )
            return self._render_submitted(request, invitation)
        if action == "fiche_incorrecte":
            try:
                submit_wrong_fiche(invitation, channel)
            except CampaignError as error:
                return self._render_form(
                    request, invitation, self._form_with_error(request, error), token
                )
            return self._render_submitted(request, invitation)
        return self._render_form(
            request,
            invitation,
            self._form_with_error(request, "Action inconnue."),
            token,
        )

    def _form_with_error(self, request, message):
        form = VerificationModificationForm(request.POST)
        form.add_error(None, str(message))
        return form