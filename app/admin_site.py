"""Site d'administration Django limité en débit sur la connexion."""
from django.contrib.admin.sites import AdminSite
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit


def _admin_rate_key(group, request) -> str:
    """Clé par adresse IP et nom de compte, comme pour la connexion applicative."""
    ip = request.META.get("REMOTE_ADDR", "")
    username = request.POST.get("username", "")
    return f"admin:{ip}:{username}"


class RateLimitedAdminSite(AdminSite):
    """Admin Django dont le formulaire de connexion est soumis à un débit maximal."""

    @method_decorator(
        ratelimit(key=_admin_rate_key, rate="10/m", method="POST", block=True)
    )
    def login(self, request, extra_context=None):
        return super().login(request, extra_context=extra_context)


admin_site = RateLimitedAdminSite(name="admin")
