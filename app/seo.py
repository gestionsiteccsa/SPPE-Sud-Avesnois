"""Bloquage de l'indexation par les moteurs de recherche."""


class NoIndexMiddleware:
    """Interdit l'indexation de toutes les réponses par un en-tête X-Robots-Tag."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault("X-Robots-Tag", "noindex, nofollow, noarchive")
        return response
