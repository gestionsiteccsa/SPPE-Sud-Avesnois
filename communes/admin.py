from django.contrib import admin
from django.contrib.admin.decorators import register

from app.admin_site import admin_site
from .models import Commune


@register(Commune, site=admin_site)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ["nom", "code_postal"]
    search_fields = ["nom", "code_postal"]
    list_filter = ["code_postal"]
