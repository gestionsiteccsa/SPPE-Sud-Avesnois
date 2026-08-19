from django.urls import path
from django.views.generic import TemplateView

from .views import CollaborateurRegistrationView

urlpatterns = [
    path(
        "inscription/",
        CollaborateurRegistrationView.as_view(),
        name="inscription",
    ),
    path(
        "inscription/envoyee/",
        TemplateView.as_view(template_name="registration/register_done.html"),
        name="inscription_done",
    ),
]
