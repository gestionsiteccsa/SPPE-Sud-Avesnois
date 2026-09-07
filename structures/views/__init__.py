from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView

from communes.models import Commune

from ..models import Structure, TypeStructure


def query_int(raw):
    """Convertit une valeur de requête HTTP en entier ; None si non numérique."""
    if raw is None or raw == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


class StructureListView(LoginRequiredMixin, ListView):
    model = Structure
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("type", "commune").filter(afficher=True)
        commune = query_int(self.request.GET.get("commune"))
        type_ = query_int(self.request.GET.get("type"))
        handicap = self.request.GET.get("handicap")
        urgence = self.request.GET.get("urgence")
        places = self.request.GET.get("places")
        q = self.request.GET.get("q")
        if commune is not None:
            qs = qs.filter(commune_id=commune)
        if type_ is not None:
            qs = qs.filter(type_id=type_)
        if handicap == "oui":
            qs = qs.filter(accueil_handicap=True)
        elif handicap == "non":
            qs = qs.filter(accueil_handicap=False)
        if urgence == "oui":
            qs = qs.filter(accueil_urgence=True)
        elif urgence == "non":
            qs = qs.filter(accueil_urgence=False)
        if places == "oui":
            qs = qs.filter(places_complet=False, places_non_communique=False, places_disponibles__gt=0)
        elif places == "complet":
            qs = qs.filter(places_complet=True)
        elif places == "non_communique":
            qs = qs.filter(places_non_communique=True)
        if q:
            qs = qs.filter(
                Q(nom__icontains=q)
                | Q(type__nom__icontains=q)
                | Q(commune__nom__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["types"] = TypeStructure.objects.all()
        ctx["communes"] = Commune.objects.all()
        ctx["filters"] = self.request.GET
        return ctx


class StructureDetailView(LoginRequiredMixin, DetailView):
    model = Structure

    def get_queryset(self):
        qs = super().get_queryset().select_related("type", "commune").filter(afficher=True)
        return qs


class StructureMapView(LoginRequiredMixin, TemplateView):
    template_name = "structures/structure_map.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        structures = Structure.objects.select_related("type", "commune").filter(
            latitude__isnull=False, longitude__isnull=False, afficher=True
        )
        features = []
        availability = {
            "available": {"label": "Disponible", "count": 0},
            "complete": {"label": "Complet", "count": 0},
            "unknown": {"label": "Non communiqué", "count": 0},
        }
        for s in structures:
            badges = []
            if s.places_complet:
                status = "complete"
                status_label = "Complet"
            elif not s.places_non_communique and s.places_disponibles:
                status = "available"
                suffix = "place" if s.places_disponibles == 1 else "places"
                status_label = f"{s.places_disponibles} {suffix}"
            else:
                status = "unknown"
                status_label = "Non communiqué"
            availability[status]["count"] += 1

            if s.accueil_handicap:
                badges.append("Handicap")
            if s.accueil_urgence:
                badges.append("Urgence")
            features.append({
                "pk": s.pk,
                "nom": s.nom_affiche,
                "type": s.type.nom if s.type else "",
                "commune": s.commune.nom if s.commune else "",
                "code_postal": s.commune.code_postal if s.commune else "",
                "age": s.afficher_age(),
                "lat": s.latitude,
                "lng": s.longitude,
                "status": status,
                "status_label": status_label,
                "badges": badges,
            })
        ctx["structures_data"] = features
        ctx["structures_count"] = len(features)
        ctx["availability"] = availability
        return ctx

