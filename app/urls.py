"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path, include

from authentication.views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetView,
)
from app.admin_site import admin_site
from app.views import health, robots_txt
from communes.admin import admin_site as _communes_admin_site  # noqa: F401
from structures.admin import admin_site as _structures_admin_site  # noqa: F401
from authentication.admin import admin_site as _authentication_admin_site  # noqa: F401

urlpatterns = [
    path('health/', health, name='health'),
    path('robots.txt', robots_txt, name='robots'),
    path(settings.ADMIN_URL, admin_site.urls),
    path("", include("home.urls")),
    path("", include("authentication.urls")),
    path("connexion/", CustomLoginView.as_view(template_name="registration/login.html"), name="login"),
    path("deconnexion/", CustomLogoutView.as_view(), name="logout"),
    path("mot-de-passe-oublie/", CustomPasswordResetView.as_view(template_name="registration/password_reset_form.html"), name="password_reset"),
    path("mot-de-passe-oublie/envoye/", auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), name="password_reset_done"),
    path("mot-de-passe-oublie/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path("mot-de-passe-oublie/termine/", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), name="password_reset_complete"),
    path("structures/", include("structures.urls")),
    path("dashboard/", include("structures.dashboard_urls")),
    path("dashboard/", include("campagnes.dashboard_urls")),
    path("", include("campagnes.urls")),
]
