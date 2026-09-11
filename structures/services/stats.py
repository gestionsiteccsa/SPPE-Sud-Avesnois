"""Calculs statistiques partagés par le tableau de bord."""

import re
from calendar import monthrange
from datetime import date
from typing import Literal, TypedDict

from django.db.models import Avg, Count, F, Q, QuerySet, Sum
from django.utils import timezone

from structures.models import JOURS_SEM, Structure


_AVAILABLE_PLACES_FILTER = Q(
    places_complet=False,
    places_non_communique=False,
    places_disponibles__isnull=False,
)

GroupField = Literal["type__nom", "commune__nom"]


class StatisticItem(TypedDict):
    label: str
    total: int


class OfferSummary(TypedDict):
    structures: int
    capacity_total: int
    capacity_average: float | None
    capacity_known: int
    capacity_missing: int
    available_places: int
    availability_known: int


class GroupedOfferStatistics(TypedDict):
    counts: list[StatisticItem]
    capacities: list[StatisticItem]


class CompletenessItem(TypedDict):
    label: str
    total: int
    missing: int
    percent: int


class DashboardStatistics(TypedDict):
    offer: OfferSummary
    by_type: GroupedOfferStatistics
    by_commune: GroupedOfferStatistics
    opening_days: list[dict]
    freshness: list[StatisticItem]
    freshness_outdated: int
    completeness: list[CompletenessItem]


def sum_available_places(base_queryset=None) -> int:
    """Somme des places disponibles hors structures complètes ou non communiquées."""
    queryset = base_queryset if base_queryset is not None else Structure.objects
    return (
        queryset.filter(_AVAILABLE_PLACES_FILTER).aggregate(
            s=Sum("places_disponibles")
        )["s"]
        or 0
    )


def _subtract_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def _collapse_distribution(
    rows: list[dict[str, object]],
    *,
    metric: str,
    missing_label: str,
    max_items: int,
) -> list[StatisticItem]:
    items: list[StatisticItem] = [
        {
            "label": str(row["label"] or missing_label),
            "total": int(row[metric] or 0),
        }
        for row in rows
    ]
    items.sort(key=lambda item: (-item["total"], item["label"].casefold()))
    if len(items) <= max_items:
        return items

    visible_items = items[: max_items - 1]
    other_total = sum(item["total"] for item in items[max_items - 1 :])
    return [*visible_items, {"label": "Autres", "total": other_total}]


def _grouped_offer_statistics(
    queryset: QuerySet,
    *,
    group_field: GroupField,
    missing_label: str,
    max_items: int,
) -> GroupedOfferStatistics:
    rows = list(
        queryset.values(label=F(group_field))
        .annotate(
            structure_count=Count("id"),
            capacity_total=Sum("nb_places_total"),
        )
        .order_by()
    )
    return {
        "counts": _collapse_distribution(
            rows,
            metric="structure_count",
            missing_label=missing_label,
            max_items=max_items,
        ),
        "capacities": _collapse_distribution(
            rows,
            metric="capacity_total",
            missing_label=missing_label,
            max_items=max_items,
        ),
    }


def _offer_summary(queryset: QuerySet) -> OfferSummary:
    values = queryset.aggregate(
        structures=Count("id"),
        capacity_total=Sum("nb_places_total"),
        capacity_average=Avg("nb_places_total"),
        capacity_known=Count("id", filter=Q(nb_places_total__isnull=False)),
        available_places=Sum(
            "places_disponibles",
            filter=_AVAILABLE_PLACES_FILTER,
        ),
        availability_known=Count("id", filter=_AVAILABLE_PLACES_FILTER),
    )
    structures = int(values["structures"] or 0)
    capacity_known = int(values["capacity_known"] or 0)
    average = values["capacity_average"]
    return {
        "structures": structures,
        "capacity_total": int(values["capacity_total"] or 0),
        "capacity_average": round(float(average), 1) if average is not None else None,
        "capacity_known": capacity_known,
        "capacity_missing": structures - capacity_known,
        "available_places": int(values["available_places"] or 0),
        "availability_known": int(values["availability_known"] or 0),
    }


def _day_schedule_entry(schedule, day: str) -> dict | None:
    """Retourne l'entrée d'horaires correspondant à un jour, ou None."""
    for item in schedule or []:
        if isinstance(item, dict) and item.get("jour") == day:
            return item
    return None


def is_open_on_day(schedule, day: str) -> bool:
    """Indique si des horaires déclarent une ouverture un jour donné."""
    entry = _day_schedule_entry(schedule, day)
    return entry is not None and entry.get("ferme") is False


def format_day_schedule(schedule, day: str) -> str:
    """Libellé court des horaires d'un jour (ex. « 08:00–12:00 »)."""
    entry = _day_schedule_entry(schedule, day)
    if entry is None or entry.get("ferme") is not False:
        return ""
    ouverture = str(entry.get("ouverture") or "").strip()
    fermeture = str(entry.get("fermeture") or "").strip()
    if ouverture and fermeture:
        return f"{ouverture}–{fermeture}"
    return "Ouvert"


JOURS_WEEKEND = {"samedi", "dimanche"}
#: Ouverture avant cette heure = horaire atypique (en minutes depuis minuit).
OUVERTURE_LIMITE_MINUTES = 7 * 60 + 30
#: Fermeture après cette heure = horaire atypique (en minutes depuis minuit).
FERMETURE_LIMITE_MINUTES = 19 * 60

_HEURE_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def _heure_en_minutes(raw: object) -> int | None:
    """Convertit « HH:MM » en minutes depuis minuit ; None si absent ou malformé."""
    match = _HEURE_RE.match(str(raw or "").strip())
    if match is None:
        return None
    heures, minutes = int(match.group(1)), int(match.group(2))
    if heures > 23 or minutes > 59:
        return None
    return heures * 60 + minutes


def raisons_horaires_atypiques(schedule) -> list[str]:
    """Raisons pour lesquelles des horaires sont atypiques (liste vide sinon).

    Atypique = ouverture le week-end (samedi/dimanche), ouverture avant 7h30
    ou fermeture après 19h. Les jours fermés et les heures vides ou
    malformées sont ignorés : on ne signale que du positif avéré.
    """
    raisons = []
    for item in schedule or []:
        if not isinstance(item, dict) or item.get("ferme") is not False:
            continue
        jour = str(item.get("jour") or "").strip()
        label_jour = dict(JOURS_SEM).get(jour, jour) or "jour inconnu"
        if jour in JOURS_WEEKEND:
            raisons.append(f"Ouvert le {label_jour.lower()}")
        ouverture_minutes = _heure_en_minutes(item.get("ouverture"))
        if (
            ouverture_minutes is not None
            and ouverture_minutes < OUVERTURE_LIMITE_MINUTES
        ):
            raisons.append(
                f"Ouverture dès {str(item.get('ouverture')).strip()} le {label_jour.lower()}"
            )
        fermeture_minutes = _heure_en_minutes(item.get("fermeture"))
        if (
            fermeture_minutes is not None
            and fermeture_minutes > FERMETURE_LIMITE_MINUTES
        ):
            raisons.append(
                f"Fermeture à {str(item.get('fermeture')).strip()} le {label_jour.lower()}"
            )
    return raisons


def a_horaires_atypiques(schedule) -> bool:
    """Indique si des horaires déclarent une ouverture atypique (week-end ou amplitude élargie)."""
    return bool(raisons_horaires_atypiques(schedule))


def _opening_day_statistics(queryset: QuerySet) -> list[dict]:
    day_labels = dict(JOURS_SEM)
    totals = {day: 0 for day in day_labels}
    schedules = queryset.values_list("horaires", flat=True).iterator(chunk_size=500)
    for schedule in schedules:
        for day in totals:
            if is_open_on_day(schedule, day):
                totals[day] += 1
    return [
        {"jour": day, "label": label, "total": totals[day]} for day, label in day_labels.items()
    ]


def _freshness_statistics(
    queryset: QuerySet,
    *,
    reference_date: date,
) -> tuple[list[StatisticItem], int]:
    three_months_ago = _subtract_months(reference_date, 3)
    six_months_ago = _subtract_months(reference_date, 6)
    twelve_months_ago = _subtract_months(reference_date, 12)
    values = queryset.aggregate(
        under_three_months=Count(
            "id",
            filter=Q(date_mise_a_jour_monenfant__gt=three_months_ago),
        ),
        three_to_six_months=Count(
            "id",
            filter=Q(
                date_mise_a_jour_monenfant__gt=six_months_ago,
                date_mise_a_jour_monenfant__lte=three_months_ago,
            ),
        ),
        six_to_twelve_months=Count(
            "id",
            filter=Q(
                date_mise_a_jour_monenfant__gte=twelve_months_ago,
                date_mise_a_jour_monenfant__lte=six_months_ago,
            ),
        ),
        over_twelve_months=Count(
            "id",
            filter=Q(date_mise_a_jour_monenfant__lt=twelve_months_ago),
        ),
        unknown=Count(
            "id",
            filter=Q(date_mise_a_jour_monenfant__isnull=True),
        ),
    )
    statistics = [
        {"label": "Moins de 3 mois", "total": values["under_three_months"]},
        {"label": "3 à 6 mois", "total": values["three_to_six_months"]},
        {"label": "6 à 12 mois", "total": values["six_to_twelve_months"]},
        {"label": "Plus d’un an", "total": values["over_twelve_months"]},
        {"label": "Date inconnue", "total": values["unknown"]},
    ]
    outdated = values["six_to_twelve_months"] + values["over_twelve_months"]
    return statistics, outdated


def _completeness_statistics(queryset: QuerySet) -> list[CompletenessItem]:
    values = queryset.aggregate(
        structures=Count("id"),
        capacity=Count("id", filter=Q(nb_places_total__isnull=False)),
        age_range=Count(
            "id",
            filter=Q(age_non_renseigne=False)
            & (Q(age_min__isnull=False) | Q(age_max__isnull=False)),
        ),
        contact=Count(
            "id",
            filter=~Q(telephone="") | ~Q(email=""),
        ),
        geolocation=Count(
            "id",
            filter=Q(latitude__isnull=False, longitude__isnull=False),
        ),
    )
    structures = int(values["structures"] or 0)
    definitions = (
        ("Capacité totale", values["capacity"]),
        ("Tranche d’âge", values["age_range"]),
        ("Téléphone ou email", values["contact"]),
        ("Géolocalisation", values["geolocation"]),
    )
    return [
        {
            "label": label,
            "total": int(total),
            "missing": structures - int(total),
            "percent": round(int(total) / structures * 100) if structures else 0,
        }
        for label, total in definitions
    ]


def build_dashboard_statistics(
    *,
    offer_queryset: QuerySet | None = None,
    quality_queryset: QuerySet | None = None,
    reference_date: date | None = None,
    group_limit: int = 10,
) -> DashboardStatistics:
    """Construit les statistiques d’offre visible et de qualité interne."""
    if group_limit < 2:
        raise ValueError("group_limit doit être supérieur ou égal à 2")
    offer = (
        offer_queryset
        if offer_queryset is not None
        else Structure.objects.filter(afficher=True)
    )
    quality = quality_queryset if quality_queryset is not None else Structure.objects.all()
    freshness, freshness_outdated = _freshness_statistics(
        quality,
        reference_date=reference_date or timezone.localdate(),
    )
    return {
        "offer": _offer_summary(offer),
        "by_type": _grouped_offer_statistics(
            offer,
            group_field="type__nom",
            missing_label="Sans type",
            max_items=group_limit,
        ),
        "by_commune": _grouped_offer_statistics(
            offer,
            group_field="commune__nom",
            missing_label="Sans commune",
            max_items=group_limit,
        ),
        "opening_days": _opening_day_statistics(offer),
        "freshness": freshness,
        "freshness_outdated": freshness_outdated,
        "completeness": _completeness_statistics(quality),
    }
