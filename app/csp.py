"""Content Security Policy appliquée avec un nonce par requête."""
import secrets

from django.conf import settings
from django.http import HttpResponseBase


def _nonce() -> str:
    return secrets.token_urlsafe(16)


class ContentSecurityPolicyMiddleware:
    """Attache un en-tête CSP à chaque réponse applicative.

    Les pages de l'application transportent leurs scripts inline via un nonce.
    L'admin Django utilise des scripts inline sans nonce : il reçoit une
    politique assouplie sur les scripts (CSP_ADMIN_POLICY) mais conserve les
    directives de confinement (frame-ancestors, object-src, base-uri, ...).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = _nonce()
        response = self.get_response(request)
        self._apply_policy(request, response)
        return response

    def _apply_policy(self, request, response: HttpResponseBase) -> None:
        if not getattr(settings, "CSP_ENABLED", True):
            return
        if "Content-Security-Policy" in response:
            return
        admin_prefix = "/" + settings.ADMIN_URL.lstrip("/")
        if request.path.startswith(admin_prefix):
            # L'admin utilise des scripts inline sans nonce : politique assouplie
            # sur les scripts uniquement (voir CSP_ADMIN_POLICY dans settings).
            policy_source = getattr(settings, "CSP_ADMIN_POLICY", "")
        else:
            policy_source = getattr(settings, "CSP_POLICY", "")
        if not policy_source:
            return
        policy = policy_source % {"nonce": request.csp_nonce}
        response["Content-Security-Policy"] = policy
