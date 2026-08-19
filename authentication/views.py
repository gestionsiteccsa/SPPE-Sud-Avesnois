from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django_ratelimit.decorators import ratelimit

from .emails import notify_admins_new_inscription
from .forms import CollaborateurRegistrationForm
from .models import CollaborateurInscription


def _login_rate_key(group, request) -> str:
    """Clé par adresse IP et nom de compte pour éviter de bloquer toute une IP partagée."""
    ip = request.META.get("REMOTE_ADDR", "")
    username = request.POST.get("username", "")
    return f"{ip}:{username}"


class CustomLoginView(LoginView):
    @method_decorator(ratelimit(key=_login_rate_key, rate="10/m", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        messages.success(
            self.request,
            f"Bon retour {user.get_full_name() or user.email}  !",
        )
        if user.is_authenticated and not user.is_superuser:
            return redirect("dashboard:structure_list")
        return response


class CustomLogoutView(LogoutView):
    http_method_names = ["post", "options"]

    def post(self, request, *args, **kwargs):
        redirect_url = self.get_success_url()
        auth_logout(request)
        messages.success(request, "Vous êtes déconnecté·e. À bientôt !")
        return redirect(redirect_url)


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"

    @method_decorator(ratelimit(key="ip", rate="10/h", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CollaborateurRegistrationView(View):
    template_name = "registration/register.html"
    done_url = "inscription_done"

    @method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {"form": CollaborateurRegistrationForm()})

    def post(self, request):
        form = CollaborateurRegistrationForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        with transaction.atomic():
            user = form.create_user()
            inscription = CollaborateurInscription.objects.create(user=user)
        dashboard_url = request.build_absolute_uri(
            reverse("dashboard:inscription_list")
        )
        notify_admins_new_inscription(inscription, dashboard_url)
        return redirect(self.done_url)
