from django import forms

from communes.models import Commune
from structures.forms import _apply_widget_attrs

from .models import UpdateCampaign, UpdateRequest, VerificationInvitation
from .services.campaign import FIELD_LABELS, PUBLIC_FIELDS

INPUT_CLASS = (
    "block w-full px-3.5 py-2.5 text-[length:var(--fs-sm)] font-sans "
    "text-[var(--color-text)] bg-[var(--color-surface)] "
    "border border-[var(--color-border-strong)] rounded-[var(--radius-md)] "
    "min-h-[2.75rem] hover:border-[var(--color-primary)] focus:outline-none "
    "focus:border-[var(--color-primary)] "
    "focus:shadow-[0_0_0_3px_var(--color-focus-ring)] "
    "transition-[border-color,box-shadow] duration-200"
)
SELECT_CLASS = INPUT_CLASS + " pr-7 appearance-none"
TEXTAREA_CLASS = INPUT_CLASS + " resize-y"
CHECKBOX_CLASS = "w-5 h-5 mt-0.5 shrink-0 accent-[var(--color-primary)]"


def clean_test_emails(value: str) -> str:
    """Valide et normalise une liste d'adresses de test séparées par des virgules."""
    addresses = [part.strip().lower() for part in value.split(",") if part.strip()]
    for address in addresses:
        forms.EmailField().clean(address)
    return ", ".join(addresses)


class UpdateCampaignForm(forms.ModelForm):
    class Meta:
        model = UpdateCampaign
        fields = ["name", "starts_at", "ends_at", "message", "test_mode", "test_emails"]
        widgets = {
            "starts_at": forms.DateInput(attrs={"type": "date"}),
            "ends_at": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 4}),
            "test_mode": forms.CheckboxInput(attrs={"class": CHECKBOX_CLASS}),
            "test_emails": forms.TextInput(attrs={"placeholder": "test1@exemple.fr, test2@exemple.fr"}),
        }
        labels = {
            "name": "Nom",
            "starts_at": "Date de début",
            "ends_at": "Date de fin",
            "message": "Message d'introduction",
            "test_mode": "Mode test (aucun e-mail réel envoyé)",
            "test_emails": "Adresses e-mail de test",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                _apply_widget_attrs(field, SELECT_CLASS)
            elif isinstance(field.widget, forms.Textarea):
                _apply_widget_attrs(field, TEXTAREA_CLASS)
            elif isinstance(field.widget, forms.CheckboxInput):
                pass
            else:
                _apply_widget_attrs(field, INPUT_CLASS)

    def clean_test_emails(self):
        return clean_test_emails(self.cleaned_data.get("test_emails", ""))

    def clean(self):
        cleaned = super().clean()
        test_mode = cleaned.get("test_mode")
        test_emails = cleaned.get("test_emails", "").strip()
        if test_mode and not test_emails:
            self.add_error(
                "test_emails",
                "Renseignez au moins une adresse e-mail de test pour activer le mode test.",
            )
        if not test_mode and test_emails:
            cleaned["test_emails"] = ""
        return cleaned


class VerificationModificationForm(forms.Form):
    """Formulaire public de proposition de modification, pré-rempli avec les valeurs actuelles."""

    telephone = forms.CharField(
        required=False,
        label="Téléphone",
        widget=forms.TextInput(attrs={"autocomplete": "tel"}),
    )
    email = forms.EmailField(
        required=False,
        label="E-mail",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    adresse = forms.CharField(
        required=False,
        label="Adresse",
        widget=forms.TextInput(attrs={"autocomplete": "street-address"}),
    )
    commune = forms.ModelChoiceField(
        required=False,
        label="Commune",
        queryset=Commune.objects.order_by("nom"),
        empty_label="—",
    )
    places_disponibles = forms.IntegerField(
        required=False,
        label="Places disponibles",
        min_value=0,
    )
    conditions_places = forms.CharField(
        required=False,
        label="Informations complémentaires",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                _apply_widget_attrs(field, SELECT_CLASS)
            elif isinstance(field.widget, forms.Textarea):
                _apply_widget_attrs(field, TEXTAREA_CLASS)
            else:
                _apply_widget_attrs(field, INPUT_CLASS)

    def changes(self) -> dict[str, str]:
        """Valeurs proposées, hors champs laissés vides (vide = inchangé)."""
        result = {}
        for field_name in PUBLIC_FIELDS:
            value = self.cleaned_data.get(field_name)
            if value is None:
                continue
            if field_name == "commune":
                result[field_name] = str(value.pk)
            else:
                result[field_name] = str(value).strip()
        return result


class AssistedRequestForm(forms.Form):
    """Saisie assistée par un agent (téléphone ou accueil) au nom de la personne."""

    invitation = forms.ModelChoiceField(
        label="Fiche concernée",
        queryset=VerificationInvitation.objects.none(),
        empty_label=None,
    )
    request_type = forms.ChoiceField(
        label="Type de demande",
        choices=[
            (UpdateRequest.REQUEST_MODIFICATION, "Proposition de modification"),
            (UpdateRequest.REQUEST_CONFIRMATION, "Confirmation sans modification"),
            (UpdateRequest.REQUEST_STOP_ACTIVITY, "N'exerce plus cette activité"),
            (UpdateRequest.REQUEST_WRONG_FICHE, "Cette fiche ne me concerne pas"),
        ],
    )
    channel = forms.ChoiceField(
        label="Canal",
        choices=[
            (VerificationInvitation.CHANNEL_PHONE, "Téléphone"),
            (VerificationInvitation.CHANNEL_RECEPTION, "Accueil physique"),
        ],
    )
    telephone = forms.CharField(required=False, label="Téléphone")
    email = forms.EmailField(required=False, label="E-mail")
    adresse = forms.CharField(required=False, label="Adresse")
    commune = forms.ModelChoiceField(
        required=False,
        label="Commune",
        queryset=Commune.objects.order_by("nom"),
        empty_label="—",
    )
    places_disponibles = forms.IntegerField(required=False, label="Places disponibles", min_value=0)
    conditions_places = forms.CharField(
        required=False,
        label="Informations complémentaires",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, invitations=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["invitation"].queryset = invitations or VerificationInvitation.objects.none()
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                _apply_widget_attrs(field, SELECT_CLASS)
            elif isinstance(field.widget, forms.Textarea):
                _apply_widget_attrs(field, TEXTAREA_CLASS)
            else:
                _apply_widget_attrs(field, INPUT_CLASS)

    def changes(self) -> dict[str, str]:
        result = {}
        for field_name in PUBLIC_FIELDS:
            value = self.cleaned_data.get(field_name)
            if value is None:
                continue
            if field_name == "commune":
                result[field_name] = str(value.pk)
            else:
                result[field_name] = str(value).strip()
        return result

    @staticmethod
    def labels() -> dict[str, str]:
        return FIELD_LABELS