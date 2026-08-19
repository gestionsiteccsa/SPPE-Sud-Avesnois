from django.http import HttpRequest, HttpResponse, JsonResponse

ROBOTS_TXT = "User-agent: *\nDisallow: /\n"


def health(request: HttpRequest) -> JsonResponse:
    """Liveness publique minimale, sans exposer la configuration interne."""
    return JsonResponse({"status": "ok"})


def robots_txt(request: HttpRequest) -> HttpResponse:
    """Interdit le crawlage du site aux moteurs de recherche."""
    return HttpResponse(ROBOTS_TXT, content_type="text/plain")
