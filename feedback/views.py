import logging
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import resolve, reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django_ratelimit.decorators import ratelimit

from .emails import notify_admins_new_feedback
from .forms import FeedbackForm

logger = logging.getLogger(__name__)


def _wants_json(request) -> bool:
    accept = request.META.get("HTTP_ACCEPT", "")
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in accept
    )


def _detect_page_auto(request) -> str:
    """Déduit la page d'origine côté serveur (Referer même hôte)."""
    referer = request.META.get("HTTP_REFERER", "")
    if not referer:
        return ""
    try:
        parsed = urlparse(referer)
    except ValueError:
        return ""
    if parsed.netloc and parsed.netloc != request.get_host().split(":")[0]:
        # Referer externe : ne pas le stocker comme page interne.
        if parsed.netloc != request.get_host():
            return ""
    path = parsed.path or ""
    if parsed.query:
        path = f"{path}?{parsed.query}"
    return path[:500]


def _resolve_url_name(path: str) -> str:
    if not path:
        return ""
    try:
        clean_path = urlparse(path).path or path
        match = resolve(clean_path)
    except Exception:  # noqa: BLE001 - page libre, le nom est décoratif
        return ""
    return (match.url_name or "")[:200]


class FeedbackSubmitView(LoginRequiredMixin, View):
    """Crée un signalement. Accepte POST HTML classique et fetch JSON."""

    template_name = "feedback/form.html"

    @method_decorator(ratelimit(key="user", rate="10/h", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        form = FeedbackForm(
            initial={"page_declaree": _detect_page_auto(request) or "/"}
        )
        if _wants_json(request):
            return JsonResponse(
                {"ok": False, "errors": {"__all__": ["Utilisez POST pour envoyer."]}},
                status=405,
            )
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = FeedbackForm(request.POST)
        if not form.is_valid():
            if _wants_json(request):
                raw_errors = form.errors or {}
                errors = {
                    field: [str(err) for err in err_list]
                    for field, err_list in raw_errors.items()
                }
                return JsonResponse({"ok": False, "errors": errors}, status=400)
            return render(request, self.template_name, {"form": form}, status=400)

        report = form.save(commit=False)
        report.user = request.user
        report.page_auto = _detect_page_auto(request)
        # Secours si aucun Referer (ouverture directe, navigation privée) :
        # le JS envoie aussi le contexte courant dans page_contexte.
        if not report.page_auto:
            fallback = (request.POST.get("page_contexte") or "")[:500]
            report.page_auto = fallback
        report.url_name = _resolve_url_name(
            report.page_auto or report.page_declaree
        )
        report.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
        report.save()

        try:
            detail_url = request.build_absolute_uri(
                reverse("admin:feedback_feedbackreport_change", args=[report.pk])
            )
        except Exception:  # noqa: BLE001 - l'admin peut être à un chemin custom
            detail_url = ""
        try:
            notify_admins_new_feedback(report, detail_url)
        except Exception:  # noqa: BLE001 - un échec email ne doit pas perdre le signalement
            logger.exception("Échec d'envoi email pour le signalement %s", report.pk)

        if _wants_json(request):
            return JsonResponse({"ok": True, "id": report.pk}, status=201)

        messages.success(request, "Merci ! Votre signalement a bien été envoyé.")
        next_url = request.POST.get("next") or request.GET.get("next") or ""
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("home")
