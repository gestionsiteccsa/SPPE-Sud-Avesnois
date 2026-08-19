"""Processeurs de contexte applicatifs."""

from authentication.models import CollaborateurInscription


def csp_nonce(request):
    """Expose le nonce CSP de la requête aux templates."""
    return {"csp_nonce": getattr(request, "csp_nonce", "")}


def pending_inscriptions(request):
    """Compte des demandes d'inscription en attente pour le menu du tableau de bord."""
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return {"pending_inscriptions_count": 0}
    count = 0
    if request.user.is_superuser:
        count = CollaborateurInscription.objects.filter(
            statut=CollaborateurInscription.STATUT_EN_ATTENTE
        ).count()
    return {"pending_inscriptions_count": count}
