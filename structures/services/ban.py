"""Géocodage via la Base Adresse Nationale (api-adresse.data.gouv.fr).

Service public français, gratuit, sans clé, adapté aux adresses de
l'Avesnois. Aucune dépendance externe : bibliothèque standard uniquement.
Les échecs sont toujours silencieux (None / liste vide).
"""

import json
import logging
import urllib.parse
import urllib.request
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)

BAN_SEARCH_URL = getattr(
    settings,
    "GEOCODE_BAN_URL",
    "https://api-adresse.data.gouv.fr/search/",
)
BAN_TIMEOUT = settings.GEOCODE_TIMEOUT
BAN_MIN_SCORE = getattr(settings, "GEOCODE_BAN_MIN_SCORE", 0.5)


def _user_agent() -> str:
    contact = getattr(settings, "DEFAULT_FROM_EMAIL", "nepasrepondre@cc-sudavesnois.fr")
    return f"SPPE-Sud-Avesnois (contact: {contact})"


def _fetch(params: dict) -> dict | None:
    query_string = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{BAN_SEARCH_URL}?{query_string}",
        headers={"User-Agent": _user_agent(), "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=BAN_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as error:  # noqa: BLE001 — échec toujours silencieux
        logger.info("Requête BAN impossible : %s", error)
        return None


def _parse_feature(feature: dict) -> dict | None:
    try:
        geometry = feature.get("geometry", {})
        coords = geometry.get("coordinates", [])
        properties = feature.get("properties", {})
        lon = float(coords[0])
        lat = float(coords[1])
        score = float(properties.get("score", 0.0))
    except (IndexError, KeyError, TypeError, ValueError):
        return None
    return {
        "label": str(properties.get("label", "")),
        "score": score,
        "latitude": lat,
        "longitude": lon,
        "postcode": str(properties.get("postcode", "")),
        "city": str(properties.get("city", "")),
        "type": str(properties.get("type", "")),
    }


@lru_cache(maxsize=512)
def ban_autocomplete(
    query: str, limit: int = 5, postcode: str = ""
) -> tuple[dict, ...]:
    """Renvoie jusqu'à `limit` suggestions BAN pour une saisie (cache mémoire)."""
    clean = " ".join(str(query or "").split())
    if len(clean) < 3 or len(clean) > 200:
        return ()
    safe_limit = max(1, min(int(limit or 5), 10))
    params: dict = {"q": clean, "limit": safe_limit, "autocomplete": 1}
    clean_postcode = "".join(ch for ch in str(postcode or "") if ch.isdigit())[:5]
    if len(clean_postcode) == 5:
        params["postcode"] = clean_postcode
    payload = _fetch(params)
    if not payload:
        return ()
    results = []
    for feature in payload.get("features", []) or []:
        parsed = _parse_feature(feature)
        if parsed and parsed["label"]:
            results.append(parsed)
    return tuple(results[:safe_limit])


@lru_cache(maxsize=512)
def ban_lookup(query: str) -> tuple[float, float] | None:
    """Renvoie (latitude, longitude) du meilleur résultat BAN ou None."""
    clean = " ".join(str(query or "").split())
    if len(clean) < 3 or len(clean) > 200:
        return None
    payload = _fetch({"q": clean, "limit": 1})
    if not payload:
        return None
    features = payload.get("features", []) or []
    if not features:
        return None
    parsed = _parse_feature(features[0])
    if parsed is None or parsed["score"] < BAN_MIN_SCORE:
        return None
    return parsed["latitude"], parsed["longitude"]
