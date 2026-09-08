import logging
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView, redirect_to_login
from django.db import transaction
from django.db.models import Count, Q, Value
from django.db.models.functions import (
    Coalesce,
    Concat,
    Lower,
    NullIf,
    Trim,
    TruncMonth,
)
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.utils.html import format_html
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django_ratelimit.decorators import ratelimit

from authentication.forms import (
    DashboardUserCreateForm,
    DashboardUserUpdateForm,
    DestinataireNotificationForm,
    ProfileForm,
)
from authentication.emails import (
    notify_collaborateur_refusee,
    notify_collaborateur_validee,
)
from authentication.models import (
    CollaborateurInscription,
    DestinataireNotification,
    UserCommune,
)
from communes.models import Commune
from structures.access import allowed_commune_ids
from structures.audit import audit_actor
from structures.forms import StructureForm
from structures.models import AUDIT_ACTIONS, AuditLog, JOURS_SEM, Structure, TypeStructure
from structures.views import query_int
from structures.services.import_data import (
    ImportDataError,
    import_rows,
    read_csv_upload,
    read_xlsx_upload,
)
from structures.services.sqlite_backup import (
    SQLiteBackupError,
    delete_sqlite_backup,
    list_sqlite_backups,
    mark_backup_verified,
    run_backup,
)
from structures.services.ban import ban_autocomplete
from structures.services.stats import (
    build_dashboard_statistics,
    format_day_schedule,
    is_open_on_day,
)


logger = logging.getLogger(__name__)
User = get_user_model()


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path())


class StructureManageAccessMixin(UserPassesTestMixin):
    """Accès superadmin (tout) ou collaborateur validé (communes liées)."""

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.is_active

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path())

    def allowed_commune_ids(self):
        """Communes accessibles ; None signifie toutes."""
        return allowed_commune_ids(self.request.user)


class DashboardHomeView(StructureManageAccessMixin, TemplateView):
    template_name = "dashboard/dashboard_home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "home"

        commune_ids = self.allowed_commune_ids()
        scoped_structures = Structure.objects.all()
        if commune_ids is not None:
            scoped_structures = scoped_structures.filter(commune_id__in=commune_ids)

        counts = scoped_structures.aggregate(
            total_structures=Count("id"),
            total_visible=Count("id", filter=Q(afficher=True)),
            total_hidden=Count("id", filter=Q(afficher=False)),
            total_complets=Count("id", filter=Q(places_complet=True)),
            total_non_communique=Count(
                "id",
                filter=Q(places_non_communique=True),
            ),
            total_handicap=Count("id", filter=Q(accueil_handicap=True)),
            total_urgence=Count("id", filter=Q(accueil_urgence=True)),
            total_recrutement=Count("id", filter=Q(recrutement=True)),
        )
        ctx.update(counts)
        if commune_ids is None:
            ctx["total_communes"] = Commune.objects.count()
        else:
            ctx["total_communes"] = Commune.objects.filter(pk__in=commune_ids).count()
        ctx["total_types"] = TypeStructure.objects.count()

        statistics = build_dashboard_statistics(
            offer_queryset=scoped_structures.filter(afficher=True),
            quality_queryset=scoped_structures,
        )
        ctx["offer_stats"] = statistics["offer"]
        ctx["total_places"] = statistics["offer"]["available_places"]
        ctx["types_count"] = statistics["by_type"]["counts"]
        ctx["communes_count"] = statistics["by_commune"]["counts"]
        ctx["capacity_by_type"] = statistics["by_type"]["capacities"]
        ctx["capacity_by_commune"] = statistics["by_commune"]["capacities"]
        ctx["opening_days"] = statistics["opening_days"]
        ctx["freshness_stats"] = statistics["freshness"]
        ctx["freshness_outdated"] = statistics["freshness_outdated"]
        ctx["completeness_stats"] = statistics["completeness"]

        recent_structures = Structure.objects.select_related("type", "commune")
        if commune_ids is not None:
            recent_structures = recent_structures.filter(commune_id__in=commune_ids)
        ctx["recent_structures"] = recent_structures.order_by("-date_mise_a_jour", "-pk")[:5]

        today = date.today()
        chart_months = []
        for offset in range(11, -1, -1):
            month = today.month - offset
            year = today.year
            while month < 1:
                month += 12
                year -= 1
            chart_months.append(date(year, month, 1))

        monthly_base = Structure.objects.filter(date_mise_a_jour__gte=chart_months[0])
        if commune_ids is not None:
            monthly_base = monthly_base.filter(commune_id__in=commune_ids)
        monthly_totals = {
            (
                row["month"].date()
                if hasattr(row["month"], "date")
                else row["month"]
            ): row["total"]
            for row in (
                monthly_base
                .annotate(month=TruncMonth("date_mise_a_jour"))
                .values("month")
                .annotate(total=Count("id"))
                .order_by("month")
            )
        }
        ctx["chart_month_data"] = [
            {
                "label": month.strftime("%m/%Y"),
                "total": monthly_totals.get(month, 0),
            }
            for month in chart_months
        ]
        ctx["chart_months"] = [item["label"] for item in ctx["chart_month_data"]]
        ctx["chart_month_counts"] = [
            item["total"] for item in ctx["chart_month_data"]
        ]
        ctx["chart_type_labels"] = [
            item["label"] for item in ctx["types_count"]
        ]
        ctx["chart_type_data"] = [item["total"] for item in ctx["types_count"]]
        ctx["chart_commune_labels"] = [
            item["label"] for item in ctx["communes_count"]
        ]
        ctx["chart_commune_data"] = [
            item["total"] for item in ctx["communes_count"]
        ]
        ctx["chart_capacity_type_labels"] = [
            item["label"] for item in ctx["capacity_by_type"]
        ]
        ctx["chart_capacity_type_data"] = [
            item["total"] for item in ctx["capacity_by_type"]
        ]
        ctx["chart_capacity_commune_labels"] = [
            item["label"] for item in ctx["capacity_by_commune"]
        ]
        ctx["chart_capacity_commune_data"] = [
            item["total"] for item in ctx["capacity_by_commune"]
        ]
        ctx["chart_opening_labels"] = [
            item["label"] for item in ctx["opening_days"]
        ]
        ctx["chart_opening_data"] = [
            item["total"] for item in ctx["opening_days"]
        ]
        return ctx


class DashboardOpeningDayView(StructureManageAccessMixin, View):
    """Liste JSON des structures ouvertes un jour donné (modale dashboard)."""

    MAX_RESULTS = 200

    def get(self, request, jour):
        day = (jour or "").strip().lower()
        labels = dict(JOURS_SEM)
        if day not in labels:
            return JsonResponse({"detail": "Jour inconnu."}, status=404)

        commune_ids = self.allowed_commune_ids()
        queryset = Structure.objects.select_related("type", "commune")
        if commune_ids is not None:
            queryset = queryset.filter(commune_id__in=commune_ids)

        matches = [
            structure
            for structure in queryset.iterator(chunk_size=500)
            if is_open_on_day(structure.horaires, day)
        ]
        matches.sort(key=lambda s: (s.nom_affiche or "").casefold())
        total = len(matches)
        page = matches[: self.MAX_RESULTS]

        results = []
        for structure in page:
            is_visible = bool(structure.afficher)
            if is_visible:
                url = reverse("structures:detail", args=[structure.pk])
            else:
                url = reverse("dashboard:structure_edit", args=[structure.pk])
            results.append(
                {
                    "id": structure.pk,
                    "nom": structure.nom_affiche,
                    "type": structure.type.nom if structure.type else "",
                    "commune": structure.commune.nom if structure.commune else "",
                    "masquee": not is_visible,
                    "horaires": format_day_schedule(structure.horaires, day),
                    "url": url,
                }
            )
        return JsonResponse(
            {
                "jour": day,
                "label": labels[day],
                "total": total,
                "truncated": total > len(results),
                "results": results,
            }
        )


SORT_MAP = {
    "nom": "nom_affichage_lower",
    "type": "type__nom",
    "commune": "commune__nom",
    "places": "places_disponibles",
    "maj": "date_mise_a_jour",
    "monenfant": "date_mise_a_jour_monenfant",
}

class DashboardStructureListView(StructureManageAccessMixin, ListView):
    template_name = "dashboard/structure_list.html"
    model = Structure
    paginate_by = 25

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("type", "commune")
            .annotate(
                nom_affichage_lower=Lower(
                    Coalesce(
                        NullIf(Trim("nom_structure"), Value("")),
                        Trim(Concat("prenom", Value(" "), "nom")),
                    )
                )
            )
        )
        q = self.request.GET.get("q")
        type_ = query_int(self.request.GET.get("type"))
        commune = query_int(self.request.GET.get("commune"))
        o = self.request.GET.get("o") or "nom"
        if q:
            qs = qs.filter(
                Q(nom__icontains=q)
                | Q(prenom__icontains=q)
                | Q(nom_structure__icontains=q)
                | Q(type__nom__icontains=q)
                | Q(commune__nom__icontains=q)
                | Q(directeur__icontains=q)
                | Q(statut__icontains=q)
            )
        if type_ is not None:
            qs = qs.filter(type_id=type_)
        if commune is not None:
            qs = qs.filter(commune_id=commune)
        if o:
            parts = o.split(".")
            raw = parts[0]
            desc = len(parts) > 1 and parts[1] == "desc"
            order_field = SORT_MAP.get(raw)
            if order_field:
                qs = qs.order_by(f"-{order_field}" if desc else order_field)
        commune_ids = self.allowed_commune_ids()
        if commune_ids is not None:
            qs = qs.filter(commune_id__in=commune_ids)
        return qs

    def _build_sort_link(self, col, label):
        params = {}
        for k, v in self.request.GET.items():
            if k not in ("o", "page"):
                params[k] = v
        is_active = self.sort_col == col
        if is_active:
            params["o"] = f"{col}.asc" if self.sort_desc else f"{col}.desc"
            rotate = "transform:rotate(180deg)" if not self.sort_desc else ""
            next_direction = "croissant" if self.sort_desc else "décroissant"
            return format_html(
                '<a class="no-underline text-inherit hover:text-[var(--color-primary-hover)] inline-flex items-center gap-1"'
                ' href="?{}" aria-label="Trier par {}, ordre {}">{} '
                '<svg class="w-3 h-3 shrink-0" style="{}" aria-hidden="true">'
                '<use href="/static/img/icons.svg#i-chevron-down"></use></svg></a>',
                urlencode(params),
                label,
                next_direction,
                label,
                rotate,
            )
        else:
            params["o"] = f"{col}.asc"
            return format_html(
                '<a class="no-underline text-inherit hover:text-[var(--color-primary-hover)]"'
                ' href="?{}" aria-label="Trier par {}, ordre croissant">{}</a>',
                urlencode(params),
                label,
                label,
            )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "structures"
        ctx["types"] = TypeStructure.objects.all()
        commune_ids = self.allowed_commune_ids()
        if commune_ids is None:
            ctx["communes"] = Commune.objects.all()
        else:
            ctx["communes"] = Commune.objects.filter(pk__in=commune_ids)
        ctx["filters"] = self.request.GET
        pagination_params = self.request.GET.copy()
        pagination_params.pop("page", None)
        ctx["pagination_query"] = pagination_params.urlencode()
        o = self.request.GET.get("o") or "nom"
        parts = o.split(".")
        self.sort_col = parts[0]
        self.sort_desc = len(parts) > 1 and parts[1] == "desc"
        ctx["sort_col"] = self.sort_col
        ctx["sort_desc"] = self.sort_desc
        ctx["sort_links"] = {
            "nom": self._build_sort_link("nom", "Nom"),
            "type": self._build_sort_link("type", "Type"),
            "commune": self._build_sort_link("commune", "Commune"),
            "places": self._build_sort_link("places", "Places"),
            "maj": self._build_sort_link("maj", "Màj"),
            "monenfant": self._build_sort_link("monenfant", "monenfant.fr"),
        }
        return ctx


class DashboardStructureCreateView(SuccessMessageMixin, StructureManageAccessMixin, CreateView):
    template_name = "dashboard/structure_form.html"
    model = Structure
    form_class = StructureForm
    success_url = reverse_lazy("dashboard:structure_list")
    success_message = 'La structure « %(nom_affiche)s » a été créée.'

    def get_success_message(self, cleaned_data):
        return self.success_message % {"nom_affiche": self.object.nom_affiche}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        commune_ids = self.allowed_commune_ids()
        if commune_ids is not None:
            form.fields["commune"].queryset = Commune.objects.filter(pk__in=commune_ids)
        return form

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "structures"
        return ctx


class DashboardStructureUpdateView(SuccessMessageMixin, StructureManageAccessMixin, UpdateView):
    template_name = "dashboard/structure_form.html"
    model = Structure
    form_class = StructureForm
    success_url = reverse_lazy("dashboard:structure_list")
    success_message = 'La structure « %(nom_affiche)s » a été mise à jour.'

    def get_success_message(self, cleaned_data):
        return self.success_message % {"nom_affiche": self.object.nom_affiche}

    def get_queryset(self):
        qs = super().get_queryset()
        commune_ids = self.allowed_commune_ids()
        if commune_ids is not None:
            qs = qs.filter(commune_id__in=commune_ids)
        return qs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        commune_ids = self.allowed_commune_ids()
        if commune_ids is not None:
            form.fields["commune"].queryset = Commune.objects.filter(pk__in=commune_ids)
        return form

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "structures"
        return ctx


class DashboardStructureDeleteView(StructureManageAccessMixin, DeleteView):
    template_name = "dashboard/structure_confirm_delete.html"
    model = Structure
    success_url = reverse_lazy("dashboard:structure_list")

    def get_queryset(self):
        qs = super().get_queryset()
        commune_ids = self.allowed_commune_ids()
        if commune_ids is not None:
            qs = qs.filter(commune_id__in=commune_ids)
        return qs

    def form_valid(self, form):
        structure_name = self.object.nom
        with audit_actor(self.request.user):
            response = super().form_valid(form)
        messages.success(
            self.request,
            f'La structure « {structure_name} » a été supprimée.',
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "structures"
        return ctx


class DashboardAddressSuggestView(StructureManageAccessMixin, View):
    """Suggestions d'adresses BAN pour l'aide à la saisie (dashboard uniquement)."""

    @method_decorator(ratelimit(key="user", rate="60/m", method="GET", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        raw_query = (request.GET.get("q") or "").strip()
        if len(raw_query) < 3 or len(raw_query) > 200:
            return JsonResponse({"results": []})
        postcode = ""
        commune_raw = request.GET.get("commune")
        try:
            commune_id = int(commune_raw) if commune_raw not in (None, "") else None
        except (TypeError, ValueError):
            commune_id = None
        if commune_id is not None:
            allowed = self.allowed_commune_ids()
            if allowed is None or commune_id in allowed:
                try:
                    commune = Commune.objects.only("code_postal", "nom").get(pk=commune_id)
                except Commune.DoesNotExist:
                    commune = None
                if commune is not None and commune.code_postal:
                    postcode = commune.code_postal
        try:
            suggestions = ban_autocomplete(raw_query, limit=5, postcode=postcode)
        except Exception as error:  # noqa: BLE001 — jamais 500 pour une aide saisie
            logger.info("Suggestions d'adresses indisponibles : %s", error)
            return JsonResponse({"results": []})
        results = [
            {
                "label": item["label"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "score": item["score"],
                "postcode": item["postcode"],
                "city": item["city"],
            }
            for item in suggestions
        ]
        return JsonResponse({"results": results})


class DashboardCommuneListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/commune_list.html"
    context_object_name = "communes"
    model = Commune

    def get_queryset(self):
        queryset = Commune.objects.annotate(structure_count=Count("structure"))
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(nom__icontains=query) | Q(code_postal__icontains=query)
            )
        return queryset.order_by("nom", "code_postal")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "communes"
        ctx["query"] = self.request.GET.get("q", "").strip()
        return ctx


class DashboardCommuneCreateView(
    SuccessMessageMixin,
    SuperuserRequiredMixin,
    CreateView,
):
    template_name = "dashboard/commune_form.html"
    model = Commune
    fields = ["nom", "code_postal"]
    success_url = reverse_lazy("dashboard:commune_list")
    success_message = 'La commune « %(nom)s » a été créée.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "communes"
        return ctx

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)


class DashboardCommuneUpdateView(
    SuccessMessageMixin,
    SuperuserRequiredMixin,
    UpdateView,
):
    template_name = "dashboard/commune_form.html"
    model = Commune
    fields = ["nom", "code_postal"]
    success_url = reverse_lazy("dashboard:commune_list")
    success_message = 'La commune « %(nom)s » a été mise à jour.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "communes"
        return ctx

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)


class DashboardCommuneDeleteView(SuperuserRequiredMixin, DeleteView):
    template_name = "dashboard/commune_confirm_delete.html"
    model = Commune
    success_url = reverse_lazy("dashboard:commune_list")

    def form_valid(self, form):
        commune_name = self.object.nom
        with audit_actor(self.request.user):
            response = super().form_valid(form)
        messages.success(
            self.request,
            f'La commune « {commune_name} » a été supprimée.',
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "communes"
        return ctx


class DashboardTypeListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/type_list.html"
    context_object_name = "types"
    model = TypeStructure

    def get_queryset(self):
        queryset = TypeStructure.objects.annotate(structure_count=Count("structure"))
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(nom__icontains=query)
        return queryset.order_by("nom")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "types"
        ctx["query"] = self.request.GET.get("q", "").strip()
        return ctx


class DashboardTypeCreateView(
    SuccessMessageMixin,
    SuperuserRequiredMixin,
    CreateView,
):
    template_name = "dashboard/type_form.html"
    model = TypeStructure
    fields = ["nom"]
    success_url = reverse_lazy("dashboard:type_list")
    success_message = 'Le type « %(nom)s » a été créé.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "types"
        return ctx

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)


class DashboardTypeUpdateView(
    SuccessMessageMixin,
    SuperuserRequiredMixin,
    UpdateView,
):
    template_name = "dashboard/type_form.html"
    model = TypeStructure
    fields = ["nom"]
    success_url = reverse_lazy("dashboard:type_list")
    success_message = 'Le type « %(nom)s » a été mis à jour.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "types"
        return ctx

    def form_valid(self, form):
        with audit_actor(self.request.user):
            return super().form_valid(form)


class DashboardTypeDeleteView(SuperuserRequiredMixin, DeleteView):
    template_name = "dashboard/type_confirm_delete.html"
    model = TypeStructure
    success_url = reverse_lazy("dashboard:type_list")

    def form_valid(self, form):
        type_name = self.object.nom
        with audit_actor(self.request.user):
            response = super().form_valid(form)
        messages.success(
            self.request,
            f'Le type « {type_name} » a été supprimé.',
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "types"
        return ctx


class DashboardImportView(SuperuserRequiredMixin, View):
    template_name = "dashboard/import_data.html"

    def get(self, request):
        return render(request, self.template_name, {"active_tab": "import"})

    MAX_FILE_SIZE = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS = {".xlsx", ".csv"}

    def post(self, request):
        fichier = request.FILES.get("fichier")
        if not fichier:
            messages.error(request, "Aucun fichier sélectionné.")
            return render(request, self.template_name, {"active_tab": "import"})

        if fichier.size > self.MAX_FILE_SIZE:
            messages.error(request, "Le fichier est trop volumineux (max 10 Mo).")
            return render(request, self.template_name, {"active_tab": "import"})

        ext = Path(fichier.name).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            messages.error(request, "Format non supporté. Utilisez .xlsx ou .csv.")
            return render(request, self.template_name, {"active_tab": "import"})

        try:
            if ext == ".xlsx":
                rows = read_xlsx_upload(fichier)
            else:
                rows = read_csv_upload(fichier)
            count = import_rows(
                rows,
                replace=request.POST.get("ecraser") == "on",
                actor=request.user,
            )
            messages.success(request, f"{count} structure(s) importée(s) avec succès.")
        except ImportDataError as error:
            messages.error(request, f"Import refusé : {error}")
        except Exception:
            logger.exception("Échec inattendu de l'import de structures")
            messages.error(
                request,
                "Une erreur inattendue a interrompu l'import. Les données existantes sont conservées.",
            )

        return render(request, self.template_name, {"active_tab": "import"})


class DashboardUserListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/user_list.html"
    context_object_name = "users"
    model = User
    queryset = User.objects.all().order_by("-date_joined")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "users"
        users = ctx["users"]
        communes_by_user = {}
        for user_id, commune_nom in UserCommune.objects.filter(
            user__in=users, commune__isnull=False
        ).values_list("user_id", "commune__nom"):
            communes_by_user.setdefault(user_id, []).append(commune_nom)
        ctx["communes_by_user"] = communes_by_user
        return ctx


class DashboardUserCreateView(SuperuserRequiredMixin, CreateView):
    template_name = "dashboard/user_form.html"
    model = User
    form_class = DashboardUserCreateForm
    success_url = reverse_lazy("dashboard:user_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "users"
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        AuditLog.objects.create(
            user=self.request.user,
            action="create",
            model_name="User",
            object_id=user.pk,
            object_repr=user.email,
            changes={
                "email": {"old": None, "new": user.email},
                "is_superuser": {"old": None, "new": user.is_superuser},
                "is_active": {"old": None, "new": user.is_active},
            },
        )
        return response


class DashboardUserUpdateView(SuperuserRequiredMixin, UpdateView):
    template_name = "dashboard/user_form.html"
    model = User
    form_class = DashboardUserUpdateForm
    success_url = reverse_lazy("dashboard:user_list")

    def _user_snapshot(self):
        user = User.objects.get(pk=self.object.pk)
        return {
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_active": user.is_active,
            "communes": sorted(
                UserCommune.objects.filter(user=user).values_list(
                    "commune__nom", flat=True
                )
            ),
        }

    def form_valid(self, form):
        before = self._user_snapshot()
        response = super().form_valid(form)
        after = self._user_snapshot()
        changes = {
            key: {"old": before[key], "new": after[key]}
            for key in before
            if before[key] != after[key]
        }
        if changes:
            AuditLog.objects.create(
                user=self.request.user,
                action="update",
                model_name="User",
                object_id=self.object.pk,
                object_repr=self.object.email,
                changes=changes,
            )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "users"
        return ctx


class DashboardUserDeleteView(SuperuserRequiredMixin, DeleteView):
    template_name = "dashboard/user_confirm_delete.html"
    model = User
    success_url = reverse_lazy("dashboard:user_list")

    def form_valid(self, form):
        is_last_superuser = (
            self.object.is_superuser
            and self.object.is_active
            and not User.objects.filter(is_superuser=True, is_active=True)
            .exclude(pk=self.object.pk)
            .exists()
        )
        if is_last_superuser:
            messages.error(
                self.request,
                "Le dernier superutilisateur actif ne peut pas être supprimé.",
            )
            return redirect(self.success_url)
        user_pk = self.object.pk
        user_email = self.object.email
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action="delete",
            model_name="User",
            object_id=user_pk,
            object_repr=user_email,
            changes={"_deleted": True},
        )
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "users"
        return ctx


class DashboardProfileView(LoginRequiredMixin, UpdateView):
    template_name = "dashboard/profile_form.html"
    model = User
    form_class = ProfileForm
    success_url = reverse_lazy("dashboard:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def _user_snapshot(self):
        user = User.objects.get(pk=self.object.pk)
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }

    def form_valid(self, form):
        before = self._user_snapshot()
        response = super().form_valid(form)
        after = self._user_snapshot()
        changes = {
            key: {"old": before[key], "new": after[key]}
            for key in before
            if before[key] != after[key]
        }
        if changes:
            AuditLog.objects.create(
                user=self.request.user,
                action="update",
                model_name="User",
                object_id=self.object.pk,
                object_repr=self.object.email,
                changes=changes,
            )
        messages.success(self.request, "Votre profil a bien été mis à jour.")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "profile"
        return ctx


class DashboardPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "dashboard/password_change_form.html"

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("dashboard:home")
        return reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action="update",
            model_name="User",
            object_id=self.request.user.pk,
            object_repr=self.request.user.email,
            changes={"_password_changed": True},
        )
        messages.success(self.request, "Votre mot de passe a bien été modifié.")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "password"
        return ctx


class DashboardAuditLogView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/audit_log.html"
    model = AuditLog
    paginate_by = 50
    ordering = ["-timestamp"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("user")
        action = self.request.GET.get("action")
        model_name = self.request.GET.get("model")
        user_id = self.request.GET.get("user")
        if action:
            qs = qs.filter(action=action)
        if model_name:
            qs = qs.filter(model_name=model_name)
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "audit"
        ctx["filters"] = self.request.GET
        ctx["action_choices"] = AUDIT_ACTIONS
        ctx["model_names"] = (
            AuditLog.objects.values_list("model_name", flat=True)
            .distinct()
            .order_by("model_name")
        )
        ctx["audited_users"] = (
            User.objects.filter(auditlog__isnull=False)
            .distinct()
            .order_by("email")
        )
        return ctx


class DashboardStructureBatchView(StructureManageAccessMixin, View):
    def post(self, request):
        ids = [pk for pk in request.POST.getlist("ids") if query_int(pk) is not None]
        action = request.POST.get("action")
        if not ids:
            messages.warning(request, "Aucune structure sélectionnée.")
            return redirect("dashboard:structure_list")
        if action == "delete":
            structures = Structure.objects.filter(pk__in=ids)
            commune_ids = self.allowed_commune_ids()
            if commune_ids is not None:
                structures = structures.filter(commune_id__in=commune_ids)
            structure_count = structures.count()
            with audit_actor(request.user):
                structures.delete()
            AuditLog.objects.create(
                user=request.user,
                action="batch",
                model_name="Structure",
                object_id=0,
                object_repr=f"Suppression groupée de {structure_count} structure(s)",
                changes={"_deleted_ids": ids, "_count": structure_count},
            )
            messages.success(
                request,
                f"{structure_count} structure{'s' if structure_count > 1 else ''} "
                f"supprimée{'s' if structure_count > 1 else ''}.",
            )
        return redirect("dashboard:structure_list")


class DashboardInscriptionListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/inscription_list.html"
    context_object_name = "inscriptions"
    model = CollaborateurInscription
    paginate_by = 25

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user", "decideur")
            .order_by("statut", "-date_demande")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "inscriptions"
        return ctx


class DashboardInscriptionDecideView(SuperuserRequiredMixin, View):
    def post(self, request, pk):
        inscription = CollaborateurInscription.objects.select_related("user").get(pk=pk)
        if inscription.statut != CollaborateurInscription.STATUT_EN_ATTENTE:
            messages.warning(request, "Cette demande a déjà été traitée.")
            return redirect("dashboard:inscription_list")

        action = request.POST.get("action")
        user = inscription.user
        if action == "valider":
            # Écritures et journal dans une même transaction ; l'e-mail part
            # après le commit pour ne pas dépendre du serveur SMTP.
            with transaction.atomic():
                inscription.statut = CollaborateurInscription.STATUT_VALIDEE
                inscription.date_decision = timezone.now()
                inscription.decideur = request.user
                inscription.save(update_fields=["statut", "date_decision", "decideur"])
                user.is_active = True
                user.save(update_fields=["is_active"])
                AuditLog.objects.create(
                    user=request.user,
                    action="update",
                    model_name="Inscription",
                    object_id=inscription.pk,
                    object_repr=user.email,
                    changes={
                        "statut": {
                            "old": CollaborateurInscription.STATUT_EN_ATTENTE,
                            "new": CollaborateurInscription.STATUT_VALIDEE,
                        },
                        "is_active": {"old": False, "new": True},
                    },
                )
            notify_collaborateur_validee(user)
            messages.success(request, f"L'inscription de {user.email} a été validée.")
        elif action == "refuser":
            with transaction.atomic():
                inscription.statut = CollaborateurInscription.STATUT_REFUSEE
                inscription.date_decision = timezone.now()
                inscription.decideur = request.user
                inscription.save(update_fields=["statut", "date_decision", "decideur"])
                AuditLog.objects.create(
                    user=request.user,
                    action="update",
                    model_name="Inscription",
                    object_id=inscription.pk,
                    object_repr=user.email,
                    changes={
                        "statut": {
                            "old": CollaborateurInscription.STATUT_EN_ATTENTE,
                            "new": CollaborateurInscription.STATUT_REFUSEE,
                        }
                    },
                )
            notify_collaborateur_refusee(user)
            messages.success(request, f"L'inscription de {user.email} a été refusée.")
        else:
            messages.error(request, "Action inconnue.")
        return redirect("dashboard:inscription_list")


def _notification_summary(destinataires):
    active_recipients = [dest for dest in destinataires if dest.actif]
    return {
        "total": len(destinataires),
        "active": len(active_recipients),
        "primary": sum(not dest.en_cci for dest in active_recipients),
        "blind_copy": sum(dest.en_cci for dest in active_recipients),
        "fallback_active": not active_recipients,
    }


class DashboardNotificationListView(SuperuserRequiredMixin, ListView):
    template_name = "dashboard/notification_list.html"
    context_object_name = "destinataires"
    model = DestinataireNotification

    def get_queryset(self):
        return super().get_queryset().order_by("-actif", "email")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        destinataires = list(ctx["destinataires"])
        ctx["destinataires"] = destinataires
        ctx["active_tab"] = "notifications"
        ctx["form"] = DestinataireNotificationForm()
        ctx["notification_summary"] = _notification_summary(destinataires)
        return ctx


class DashboardNotificationAddView(SuperuserRequiredMixin, View):
    template_name = "dashboard/notification_list.html"

    def post(self, request):
        form = DestinataireNotificationForm(request.POST)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action="create",
                model_name="Notification",
                object_id=form.instance.pk,
                object_repr=form.instance.email,
                changes={
                    "email": {"old": None, "new": form.instance.email},
                    "actif": {"old": None, "new": form.instance.actif},
                    "en_cci": {"old": None, "new": form.instance.en_cci},
                },
            )
            messages.success(
                request, f"L'adresse {form.instance.email} a été ajoutée."
            )
            return redirect("dashboard:notification_list")
        destinataires = list(
            DestinataireNotification.objects.order_by("-actif", "email")
        )
        context = {
            "destinataires": destinataires,
            "form": form,
            "active_tab": "notifications",
            "notification_summary": _notification_summary(destinataires),
        }
        return render(request, self.template_name, context)


class DashboardNotificationUpdateView(SuperuserRequiredMixin, View):
    def post(self, request):
        def _as_pks(values):
            pks = set()
            for value in values:
                try:
                    pks.add(int(value))
                except ValueError:
                    continue
            return pks

        actifs = _as_pks(request.POST.getlist("actif"))
        en_cci = _as_pks(request.POST.getlist("en_cci"))
        dests = list(DestinataireNotification.objects.all())
        changes_by_dest = {}
        for dest in dests:
            before = (dest.actif, dest.en_cci)
            dest.actif = dest.pk in actifs
            dest.en_cci = dest.pk in en_cci
            if before != (dest.actif, dest.en_cci):
                changes_by_dest[dest] = {
                    "actif": {"old": before[0], "new": dest.actif},
                    "en_cci": {"old": before[1], "new": dest.en_cci},
                }
        if dests:
            DestinataireNotification.objects.bulk_update(dests, ["actif", "en_cci"])
            for dest, changes in changes_by_dest.items():
                AuditLog.objects.create(
                    user=request.user,
                    action="update",
                    model_name="Notification",
                    object_id=dest.pk,
                    object_repr=dest.email,
                    changes=changes,
                )
            messages.success(request, "Les préférences de notification ont été enregistrées.")
        else:
            messages.warning(request, "Aucune adresse à mettre à jour.")
        return redirect("dashboard:notification_list")


class DashboardNotificationDeleteView(SuperuserRequiredMixin, DeleteView):
    model = DestinataireNotification
    template_name = "dashboard/notification_confirm_delete.html"
    success_url = reverse_lazy("dashboard:notification_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "notifications"
        return context

    def form_valid(self, form):
        dest_pk = self.object.pk
        dest_email = self.object.email
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action="delete",
            model_name="Notification",
            object_id=dest_pk,
            object_repr=dest_email,
            changes={"_deleted": True},
        )
        messages.success(
            self.request,
            f"L'adresse {dest_email} a été supprimée.",
        )
        return response


class DashboardBackupListView(SuperuserRequiredMixin, TemplateView):
    template_name = "dashboard/backup_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["active_tab"] = "backups"
        ctx["backup_retention"] = settings.BACKUP_RETENTION
        backup_dir = Path(settings.BACKUP_DIR)
        if not backup_dir.is_dir():
            ctx["backup_error"] = (
                "Le répertoire de sauvegarde n'existe pas encore. "
                "Il sera créé à la première sauvegarde."
            )
            return ctx
        try:
            ctx["backups"] = list_sqlite_backups(backup_dir)
        except OSError as error:
            logger.warning("Répertoire de sauvegarde inaccessible : %s", error)
            ctx["backup_error"] = "Le répertoire de sauvegarde est inaccessible."
            return ctx
        if ctx["backups"]:
            newest = ctx["backups"][0]
            ctx["newest_backup"] = newest
            ctx["backup_fresh"] = (
                newest.created is not None
                and timezone.now() - newest.created < timedelta(hours=26)
            )
        return ctx


class DashboardBackupCreateView(SuperuserRequiredMixin, View):
    @method_decorator(ratelimit(key="user", rate="12/h", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            result = run_backup(
                Path(settings.DATABASES["default"]["NAME"]),
                Path(settings.BACKUP_DIR),
                keep=settings.BACKUP_RETENTION,
                environment=settings.ENVIRONMENT,
            )
        except SQLiteBackupError as error:
            logger.warning("Sauvegarde manuelle impossible : %s", error)
            messages.error(
                request,
                "La sauvegarde n'a pas pu être créée. Consultez les journaux serveur.",
            )
            return redirect("dashboard:backup_list")
        AuditLog.objects.create(
            user=request.user,
            action="create",
            model_name="BackupSQLite",
            object_id=0,
            object_repr=result.path.name,
            changes={"size": result.size, "sha256": result.sha256},
        )
        messages.success(
            request,
            f"Sauvegarde créée : {result.path.name} ({result.size} octets).",
        )
        return redirect("dashboard:backup_list")


class DashboardBackupVerifyView(SuperuserRequiredMixin, View):
    @method_decorator(ratelimit(key="user", rate="12/h", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, name):
        try:
            sha256, _size = mark_backup_verified(Path(settings.BACKUP_DIR), name)
        except SQLiteBackupError as error:
            logger.warning("Vérification de sauvegarde impossible : %s", error)
            messages.error(
                request,
                "La vérification a échoué : fichier absent ou invalide.",
            )
            return redirect("dashboard:backup_list")
        messages.success(
            request,
            f"Sauvegarde {name} valide (sha256={sha256[:16]}…).",
        )
        return redirect("dashboard:backup_list")


class DashboardBackupDeleteView(SuperuserRequiredMixin, TemplateView):
    template_name = "dashboard/backup_confirm_delete.html"

    def _find_backup(self, name):
        try:
            return next(
                (
                    backup
                    for backup in list_sqlite_backups(Path(settings.BACKUP_DIR))
                    if backup.name == name
                ),
                None,
            )
        except OSError:
            return None

    def get(self, request, name):
        backup = self._find_backup(name)
        if backup is None:
            messages.error(request, "Sauvegarde introuvable.")
            return redirect("dashboard:backup_list")
        return render(
            request,
            self.template_name,
            {"backup": backup, "active_tab": "backups"},
        )

    @method_decorator(ratelimit(key="user", rate="12/h", method="POST", block=True))
    def post(self, request, name):
        try:
            delete_sqlite_backup(Path(settings.BACKUP_DIR), name)
        except SQLiteBackupError as error:
            logger.warning("Suppression de sauvegarde impossible : %s", error)
            messages.error(
                request,
                "La sauvegarde n'a pas pu être supprimée.",
            )
            return redirect("dashboard:backup_list")
        AuditLog.objects.create(
            user=request.user,
            action="delete",
            model_name="BackupSQLite",
            object_id=0,
            object_repr=name,
            changes={},
        )
        messages.success(request, f"Sauvegarde {name} supprimée.")
        return redirect("dashboard:backup_list")
