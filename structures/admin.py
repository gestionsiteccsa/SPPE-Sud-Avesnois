from django.contrib import admin
from django.contrib.admin.decorators import register

from app.admin_site import admin_site
from .models import Structure, TypeStructure


@register(TypeStructure, site=admin_site)
class TypeStructureAdmin(admin.ModelAdmin):
    list_display = ["nom"]
    search_fields = ["nom"]


@register(Structure, site=admin_site)
class StructureAdmin(admin.ModelAdmin):
    list_display = ["nom_affiche", "type", "commune", "afficher_places", "afficher_handicap", "date_mise_a_jour"]
    list_filter = ["type", "commune", "accueil_handicap", "accueil_urgence", "places_complet"]
    search_fields = ["nom", "prenom", "nom_structure", "adresse", "email", "telephone"]
    autocomplete_fields = ["commune", "type"]
    readonly_fields = ["date_mise_a_jour"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("type", "commune")
