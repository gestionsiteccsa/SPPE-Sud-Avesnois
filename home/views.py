from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from communes.models import Commune
from structures.models import Structure


@login_required
def index(request):
    communes = Commune.objects.order_by("code_postal", "nom")
    structures = Structure.objects.filter(afficher=True)

    ctx = {
        "total_structures": structures.count(),
        "communes": list(communes),
    }
    return render(request, "home/index.html", ctx)


class DataProtectionView(LoginRequiredMixin, TemplateView):
    template_name = "home/data_protection.html"
