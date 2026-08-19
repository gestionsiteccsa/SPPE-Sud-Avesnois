from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import AbstractUser

from communes.models import Commune
from .models import DestinataireNotification, UserCommune


User = get_user_model()


def _clean_unique_email(form: forms.ModelForm) -> str:
    email = User.objects.normalize_email(form.cleaned_data["email"])
    queryset = User.objects.filter(email__iexact=email)
    if form.instance.pk:
        queryset = queryset.exclude(pk=form.instance.pk)
    if queryset.exists():
        raise forms.ValidationError("Un compte utilise déjà cette adresse email.")
    return email


class DestinataireNotificationForm(forms.ModelForm):
    class Meta:
        model = DestinataireNotification
        fields = ["email", "actif", "en_cci"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"autocomplete": "email", "autocapitalize": "none"}
            ),
        }


class DashboardUserCreateForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse email")
    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["email", "is_superuser", "is_active"]

    def clean_email(self) -> str:
        return _clean_unique_email(self)

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        if password2:
            candidate = User(email=self.cleaned_data.get("email", ""))
            password_validation.validate_password(password2, candidate)
        return password2

    def save(self, commit: bool = True) -> AbstractUser:
        user = super().save(commit=False)
        user.email = User.objects.normalize_email(user.email)
        user.username = user.email
        user.is_staff = user.is_superuser
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse email")
    current_password = forms.CharField(
        label="Mot de passe actuel",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
        help_text="Requis pour confirmer un changement d'adresse email.",
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
        }

    def clean_email(self) -> str:
        return _clean_unique_email(self)

    def clean_current_password(self) -> str:
        password = self.cleaned_data["current_password"]
        if not self.instance.check_password(password):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return password

    def save(self, commit: bool = True) -> AbstractUser:
        user = super().save(commit=False)
        user.email = User.objects.normalize_email(user.email)
        user.username = user.email
        if commit:
            user.save()
        return user


class CollaborateurRegistrationForm(forms.Form):
    prenom = forms.CharField(
        label="Prénom",
        max_length=150,
        strip=True,
        widget=forms.TextInput(attrs={"autocomplete": "given-name"}),
    )
    nom = forms.CharField(
        label="Nom",
        max_length=150,
        strip=True,
        widget=forms.TextInput(attrs={"autocomplete": "family-name"}),
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autocapitalize": "none"}),
    )
    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_email(self) -> str:
        email = User.objects.normalize_email(self.cleaned_data["email"])
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte utilise déjà cette adresse email.")
        return email

    def clean_password2(self) -> str:
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        if password2:
            candidate = User(email=self.cleaned_data.get("email", ""))
            password_validation.validate_password(password2, candidate)
        return password2

    def create_user(self) -> AbstractUser:
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["prenom"].strip(),
            last_name=self.cleaned_data["nom"].strip(),
            is_active=False,
        )
        return user


class DashboardUserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse email")
    communes = forms.ModelMultipleChoiceField(
        queryset=Commune.objects.all().order_by("nom"),
        label="Communes liées",
        required=False,
        help_text="Le collaborateur pourra ajouter et modifier les structures de ces communes.",
        widget=forms.SelectMultiple(attrs={"size": 8}),
    )

    class Meta:
        model = User
        fields = ["email", "is_superuser", "is_active"]

    def clean_email(self) -> str:
        return _clean_unique_email(self)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["communes"].initial = UserCommune.objects.filter(
                user=self.instance
            ).values_list("commune_id", flat=True)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean()
        removes_last_superuser = (
            self.instance.pk
            and self.instance.is_superuser
            and self.instance.is_active
            and (
                not cleaned.get("is_superuser", False)
                or not cleaned.get("is_active", False)
            )
            and not User.objects.filter(is_superuser=True, is_active=True)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if removes_last_superuser:
            raise forms.ValidationError(
                "Le dernier superutilisateur actif ne peut pas être désactivé ni rétrogradé."
            )
        return cleaned

    def save(self, commit: bool = True) -> AbstractUser:
        user = super().save(commit=False)
        user.email = User.objects.normalize_email(user.email)
        user.username = user.email
        user.is_staff = user.is_superuser
        if commit:
            user.save()
            self.save_communes()
        return user

    def save_communes(self) -> None:
        UserCommune.objects.filter(user=self.instance).delete()
        UserCommune.objects.bulk_create(
            UserCommune(user=self.instance, commune=commune)
            for commune in self.cleaned_data.get("communes", [])
        )
