from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from structures.access import allowed_commune_ids
from structures.audit import audit_actor

from ..forms import AssistedRequestForm, UpdateCampaignForm, clean_test_emails
from ..models import UpdateCampaign, UpdateRequest, VerificationInvitation
from ..services.campaign import (
    FIELD_LABELS,
    CampaignError,
    campaign_stats,
    close_campaign,
    create_assisted_request,
    generate_letters,
    go_live,
    launch_campaign,
    remind_unanswered,
    review_request,
)

REQUEST_FILTERS = {
    "sans_reponse": {"status__in": VerificationInvitation.STATUS_UNANSWERED},
    "sans_email": {"delivery_channel": VerificationInvitation.CHANNEL_LETTER},
    "erreur_envoi": {"status": VerificationInvitation.STATUS_SEND_ERROR},
    "modification": {"status": VerificationInvitation.STATUS_PENDING_REVIEW},
    "validation": {"requests__status": UpdateRequest.STATUS_PENDING},
    "confirme": {"status": VerificationInvitation.STATUS_CONFIRMED},
    "expire": {"status": VerificationInvitation.STATUS_EXPIRED},
}

REQUEST_SECTIONS = [
    (UpdateRequest.REQUEST_MODIFICATION, "Proposition de modification"),
    (UpdateRequest.REQUEST_STOP_ACTIVITY, "Arrêt d'activité"),
    (UpdateRequest.REQUEST_WRONG_FICHE, "Cette fiche ne me concerne pas"),
    (UpdateRequest.REQUEST_CONFIRMATION, "Confirmation sans modification"),
]

ASSISTED_INVITATION_LIMIT = 500


class CampaignManageMixin(UserPassesTestMixin):
    """Gestion des campagnes réservée aux superutilisateurs."""

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(self.request.get_full_path())


class DashboardCampaignListView(CampaignManageMixin, ListView):
    template_name = "dashboard/campaign_list.html"
    context_object_name = "campaigns"
    model = UpdateCampaign
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "campaigns"
        return ctx


class DashboardCampaignCreateView(SuccessMessageMixin, CampaignManageMixin, CreateView):
    template_name = "dashboard/campaign_form.html"
    form_class = UpdateCampaignForm
    success_url = reverse_lazy("dashboard_campagnes:campaign_list")
    success_message = "La campagne « %(name)s » a été créée."

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "campaigns"
        return ctx

    def form_valid(self, form):
        with audit_actor(self.request.user):
            form.instance.created_by = self.request.user
            response = super().form_valid(form)
        return response


class DashboardCampaignDetailView(CampaignManageMixin, DetailView):
    template_name = "dashboard/campaign_detail.html"
    context_object_name = "campaign"
    model = UpdateCampaign

    def get_queryset(self):
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "campaigns"
        ctx["stats"] = campaign_stats(self.object)
        ctx["field_labels"] = FIELD_LABELS
        invitations = self.object.invitations.select_related(
            "structure__type", "structure__commune"
        )
        status_filter = self.request.GET.get("filtre", "")
        if status_filter in REQUEST_FILTERS:
            invitations = invitations.filter(**REQUEST_FILTERS[status_filter])
        elif status_filter == "tout":
            pass
        ctx["invitations_total"] = invitations.count()
        ctx["invitations"] = invitations[:200]
        ctx["filters"] = REQUEST_FILTERS.keys()
        ctx["active_filter"] = status_filter
        return ctx


class DashboardCampaignLaunchView(CampaignManageMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        try:
            with audit_actor(request.user):
                count = launch_campaign(campaign)
            messages.success(
                request,
                f"Campagne lancée : {count} invitation{'s' if count > 1 else ''} "
                f"créée{'s' if count > 1 else ''}.",
            )
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)


class DashboardCampaignTestLaunchView(CampaignManageMixin, View):
    """Lance une campagne en brouillon en mode test, vers des adresses de test."""

    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        raw = request.POST.get("test_emails", "")
        try:
            test_emails = clean_test_emails(raw)
        except ValidationError:
            messages.error(request, "Adresse(s) e-mail de test invalide(s).")
            return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)
        if not test_emails:
            messages.error(
                request, "Renseignez au moins une adresse e-mail de test."
            )
            return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)
        try:
            with audit_actor(request.user):
                campaign.test_mode = True
                campaign.test_emails = test_emails
                campaign.save(update_fields=["test_mode", "test_emails"])
                count = launch_campaign(campaign)
            messages.success(
                request,
                f"Mode test : {count} invitation{'s' if count > 1 else ''} "
                f"envoyée{'s' if count > 1 else ''} aux adresses de test, "
                f"aucun e-mail réel envoyé.",
            )
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)


class DashboardCampaignRemindView(CampaignManageMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        try:
            with audit_actor(request.user):
                count = remind_unanswered(campaign)
            messages.success(request, f"{count} relance(s) envoyée(s).")
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)


class DashboardCampaignGoLiveView(CampaignManageMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        try:
            with audit_actor(request.user):
                count = go_live(campaign)
            messages.success(
                request,
                f"Campagne passée en réel : {count} invitation(s) renvoyée(s) "
                f"aux vraies adresses, liens de test invalidés.",
            )
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)


class DashboardCampaignLettersView(CampaignManageMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        try:
            batch = generate_letters(campaign)
        except CampaignError as error:
            messages.error(request, str(error))
            return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)
        letters = [
            {
                "invitation": invitation,
                "token": raw_token,
                "url": f"/verification/{raw_token}/",
            }
            for invitation, raw_token in batch
        ]
        return render(
            request,
            "dashboard/campaign_letters.html",
            {"campaign": campaign, "letters": letters},
        )


class DashboardCampaignCloseView(CampaignManageMixin, View):
    def post(self, request, pk):
        campaign = get_object_or_404(UpdateCampaign, pk=pk)
        try:
            with audit_actor(request.user):
                expired = close_campaign(campaign)
            messages.success(
                request,
                f"Campagne clôturée : {expired} fiche(s) sans réponse marquée(s) expirée(s).",
            )
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:campaign_detail", pk=campaign.pk)


def _scoped_invitations(user):
    invitations = VerificationInvitation.objects.select_related(
        "campaign", "structure__commune", "structure__type"
    ).order_by("-campaign__created_at", "structure__nom_structure", "structure__nom", "structure__prenom")
    commune_ids = allowed_commune_ids(user)
    if commune_ids is not None:
        invitations = invitations.filter(structure__commune_id__in=commune_ids)
    return invitations


class DashboardRequestQueueView(UserPassesTestMixin, ListView):
    template_name = "dashboard/request_queue.html"
    context_object_name = "requests"
    model = UpdateRequest
    paginate_by = 25

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.is_active

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(self.request.get_full_path())

    def _filtered_requests(self):
        """Filtres partagés entre la page paginée et les compteurs globaux."""
        queryset = UpdateRequest.objects.all()
        commune_ids = allowed_commune_ids(self.request.user)
        if commune_ids is not None:
            queryset = queryset.filter(
                invitation__structure__commune_id__in=commune_ids
            )
        categorie = self.request.GET.get("categorie", "")
        if categorie in {value for value, _label in UpdateRequest.REQUEST_CHOICES}:
            queryset = queryset.filter(request_type=categorie)
        statut = self.request.GET.get("statut", "")
        if statut == "en_attente":
            queryset = queryset.filter(status=UpdateRequest.STATUS_PENDING).exclude(
                request_type=UpdateRequest.REQUEST_CONFIRMATION
            )
        elif statut in (UpdateRequest.STATUS_ACCEPTED, UpdateRequest.STATUS_REJECTED):
            queryset = queryset.filter(status=statut)
        campagne = self.request.GET.get("campagne", "")
        if campagne.isdigit():
            queryset = queryset.filter(invitation__campaign_id=int(campagne))
        q = self.request.GET.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(invitation__structure__nom__icontains=q)
                | Q(invitation__structure__prenom__icontains=q)
                | Q(invitation__structure__nom_structure__icontains=q)
            )
        return queryset

    def get_queryset(self):
        return (
            self._filtered_requests()
            .select_related(
                "invitation__campaign",
                "invitation__structure__commune",
                "invitation__structure__type",
                "reviewed_by",
                "created_by",
            )
            .prefetch_related("fields")
            .order_by("request_type", "-submitted_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "request_queue"
        ctx["field_labels"] = FIELD_LABELS
        invitations = _scoped_invitations(self.request.user)
        ctx["assisted_invitation_count"] = invitations.count()
        ctx["assisted_invitation_limit"] = ASSISTED_INVITATION_LIMIT
        ctx["assisted_form"] = AssistedRequestForm(
            invitations=invitations[:ASSISTED_INVITATION_LIMIT]
        )
        # Les sections affichent la page courante ; les compteurs restent globaux.
        requests = list(ctx["object_list"])
        global_counts = dict(
            self._filtered_requests()
            .values_list("request_type")
            .annotate(total=Count("id"))
        )
        ctx["sections"] = [
            {
                "type": request_type,
                "label": label,
                "count": global_counts.get(request_type, 0),
                "requests": [r for r in requests if r.request_type == request_type],
            }
            for request_type, label in REQUEST_SECTIONS
        ]
        ctx["categories"] = UpdateRequest.REQUEST_CHOICES
        ctx["campaigns"] = UpdateCampaign.objects.order_by("-starts_at", "-created_at")
        pagination_params = self.request.GET.copy()
        pagination_params.pop("page", None)
        ctx["pagination_query"] = pagination_params.urlencode()
        ctx["filters"] = {
            "categorie": self.request.GET.get("categorie", ""),
            "statut": self.request.GET.get("statut", ""),
            "campagne": self.request.GET.get("campagne", ""),
            "q": self.request.GET.get("q", ""),
        }
        return ctx


class DashboardRequestReviewView(UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.is_active

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(self.request.get_full_path())

    def post(self, request, pk):
        review = get_object_or_404(
            UpdateRequest.objects.select_related("invitation__structure"), pk=pk
        )
        commune_ids = allowed_commune_ids(request.user)
        if (
            commune_ids is not None
            and review.invitation.structure.commune_id not in commune_ids
        ):
            messages.error(request, "Vous n'avez pas accès à cette demande.")
            return redirect("dashboard_campagnes:request_queue")
        decision = request.POST.get("decision", "")
        accepted_ids = [int(pk) for pk in request.POST.getlist("accepted_fields")]
        comment = request.POST.get("comment", "")
        try:
            with audit_actor(request.user):
                review_request(review, decision, accepted_ids, comment, request.user)
            messages.success(request, "La demande a été traitée.")
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:request_queue")


class DashboardAssistedRequestView(UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.is_active

    def handle_no_permission(self):
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(self.request.get_full_path())

    def post(self, request):
        form = AssistedRequestForm(
            request.POST,
            invitations=_scoped_invitations(request.user),
        )
        if not form.is_valid():
            messages.error(request, "Vérifiez les informations saisies.")
            return redirect("dashboard_campagnes:request_queue")
        invitation = form.cleaned_data["invitation"]
        try:
            with audit_actor(request.user):
                create_assisted_request(
                    invitation,
                    form.cleaned_data["request_type"],
                    form.changes(),
                    form.cleaned_data["channel"],
                    request.user,
                )
            messages.success(
                request,
                f"La demande pour « {invitation.structure} » a été enregistrée.",
            )
        except CampaignError as error:
            messages.error(request, str(error))
        return redirect("dashboard_campagnes:request_queue")