"""Personnalisation de l'admin Django pour garantir une adresse email unique.

Le chemin d'accès par défaut de l'admin ne vérifiait pas l'unicité de l'email
(auth.User n'a pas de contrainte unique). Le backend d'authentification est déjà
fermé sur doublon ; cette page administrateur applique la même règle pour que
l'email reste une identité fiable dans tous les chemins de création.
"""
from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from app.admin_site import admin_site
from .forms import _clean_unique_email
from .models import DestinataireNotification

User = get_user_model()


class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="Adresse email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def clean_email(self):
        return _clean_unique_email(self)

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = User.objects.normalize_email(user.email)
        user.username = user.email
        if commit:
            user.save()
        return user


class AdminUserChangeForm(UserChangeForm):
    email = forms.EmailField(label="Adresse email")

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"

    def clean_email(self):
        return _clean_unique_email(self)

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = User.objects.normalize_email(user.email)
        user.username = user.email
        if commit:
            user.save()
            self.save_m2m()
        return user


@register(User, site=admin_site)
class BddPeUserAdmin(DjangoUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates importantes", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("email", "is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("email", "username")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")


@register(DestinataireNotification, site=admin_site)
class DestinataireNotificationAdmin(ModelAdmin):
    list_display = ("email", "actif", "en_cci")
    list_filter = ("actif", "en_cci")
    search_fields = ("email",)
