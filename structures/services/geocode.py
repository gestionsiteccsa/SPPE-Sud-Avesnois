"""Géocodage des structures via OpenStreetMap/Nominatim.

Aucune dépendance externe : on utilise uniquement la bibliothèque standard.
Les échecs (réseau, HTTP, résultat vide) sont toujours silencieux : une fiche
non géolocalisable reste enregistrable et n'apparaît simplement pas sur la carte.
"""

import json
import logging
import time
import unicodedata
import urllib.parse
import urllib.request
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
GEOCODE_TIMEOUT = settings.GEOCODE_TIMEOUT
GEOCODE_RATE_LIMIT_SECONDS = getattr(settings, "GEOCODE_RATE_LIMIT_SECONDS", 1.1)

_last_request_ts = 0.0


def _user_agent() -> str:
    contact = getattr(settings, "DEFAULT_FROM_EMAIL", "nepasrepondre@cc-sudavesnois.fr")
    return f"SPPE-Sud-Avesnois (contact: {contact})"


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def _respect_rate_limit() -> None:
    """Espace les appels vers Nominatim pour respecter sa politique d'usage."""
    global _last_request_ts
    elapsed = time.monotonic() - _last_request_ts
    if elapsed < GEOCODE_RATE_LIMIT_SECONDS:
        time.sleep(GEOCODE_RATE_LIMIT_SECONDS - elapsed)
    _last_request_ts = time.monotonic()


@lru_cache(maxsize=256)
def _lookup(query: str) -> tuple[float, float] | None:
    """Interroge Nominatim et renvoie (latitude, longitude) ou None."""
    _respect_rate_limit()
    params = urllib.parse.urlencode(
        {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "fr",
        }
    )
    request = urllib.request.Request(
        f"{GEOCODE_URL}?{params}",
        headers={"User-Agent": _user_agent(), "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=GEOCODE_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as error:  # noqa: BLE001 — échec toujours silencieux
        logger.info("Géocodage impossible pour %r : %s", query, error)
        return None
    if not payload:
        return None
    try:
        return float(payload[0]["lat"]), float(payload[0]["lon"])
    except (KeyError, TypeError, ValueError):
        return None


def build_query(structure) -> str:
    """Construit une requête de recherche à partir de l'adresse et de la commune."""
    parts = [structure.adresse.strip()]
    if structure.commune_id:
        commune = structure.commune
        commune_part = commune.nom
        if commune.code_postal:
            commune_part = f"{commune.code_postal} {commune.nom}"
        parts.append(commune_part)
    query = ", ".join(part for part in parts if part).strip()
    return query or structure.nom_affiche


def geocode_structure(structure) -> None:
    """Renseigne latitude/longitude si absentes, sans jamais lever d'exception."""
    if not settings.GEOCODE_ENABLED:
        return
    if structure.latitude is not None and structure.longitude is not None:
        return
    query = _normalize(build_query(structure))
    if not query:
        return
    result = _lookup(query)
    if result is None:
        return
    structure.latitude, structure.longitude = result