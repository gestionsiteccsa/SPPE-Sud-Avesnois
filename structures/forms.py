import re
import unicodedata

from django import forms

from .models import JOURS_SEM, Structure, TypeStructure
from .services.geocode import geocode_structure


JOURS_SEM_DICT = dict(JOURS_SEM)

PHONE_RE = re.compile(r"^(?:\+33|0033|0)([1-9])(?:\d{2}){4}$")

INPUT_CLASS = "field__input"
SELECT_CLASS = "field__select"
TEXTAREA_CLASS = "field__textarea"
CHECKBOX_CLASS = "field__check__input"


def _apply_widget_attrs(field, class_name, *, input_type=None):
    """Injecte la classe CSS voulue dans le widget d'un champ, en préservant les attrs existants."""
    attrs = field.widget.attrs
    existing = attrs.get("class", "")
    if class_name and class_name not in existing:
        attrs["class"] = f"{existing} {class_name}".strip() if existing else class_name


class TriStateSelect(forms.Select):
    """Select à trois états (None / True / False) pour les champs BooleanField(null=True)."""

    def __init__(self, attrs=None):
        choices = (
            ("", "Non concerné"),
            ("true", "Oui"),
            ("false", "Non"),
        )
        super().__init__(attrs=attrs, choices=choices)


def _normalize_name(value: str) -> str:
    """Minuscules, sans accents ni espaces superflus, pour comparer des noms."""
    normalized = unicodedata.normalize("NFKD", value)
    stripped = "".join(c for c in normalized if not unicodedata.combining(c))
    return " ".join(stripped.lower().split())


def _normalize_email(value: str) -> str:
    """Espace, minuscules : stocke les emails de façon homogène."""
    if value is None:
        return ""
    return str(value).strip().lower()


def _normalize_phone(value: str) -> str:
    """Normalise un numéro de téléphone français au format national 0X XX XX XX XX."""
    digits = re.sub(r"[^\d+]", "", str(value or ""))
    if not digits:
        return ""
    if not PHONE_RE.match(digits):
        raise forms.ValidationError(
            "Saisissez un numéro de téléphone français valide, "
            "par exemple 01 23 45 67 89 ou +33 1 23 45 67 89."
        )
    if digits.startswith("+33"):
        digits = "0" + digits[3:]
    elif digits.startswith("0033"):
        digits = "0" + digits[4:]
    return " ".join([digits[0:2]] + [digits[i : i + 2] for i in range(2, 10, 2)])


class StructureForm(forms.ModelForm):
    est_structure = forms.BooleanField(
        required=False,
        label="Vous êtes une structure ?",
    )
    type_nom = forms.CharField(
        required=False,
        label="Nouveau type",
        help_text="Si le type n'existe pas, saisissez-le ici pour le créer automatiquement.",
    )

    class Meta:
        model = Structure
        exclude = ["date_mise_a_jour"]
        widgets = {
            "horaires": forms.HiddenInput(),
            "horaires_notes": forms.Textarea(attrs={"rows": 2}),
            "conditions_places": forms.Textarea(attrs={"rows": 2}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "accueil_handicap": TriStateSelect(),
            "accueil_urgence": TriStateSelect(),
            "recrutement": TriStateSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                _apply_widget_attrs(field, CHECKBOX_CLASS)
            elif isinstance(widget, forms.Select):
                _apply_widget_attrs(field, SELECT_CLASS)
            elif isinstance(widget, forms.Textarea):
                _apply_widget_attrs(field, TEXTAREA_CLASS)
            elif isinstance(widget, forms.HiddenInput):
                pass
            else:
                _apply_widget_attrs(field, INPUT_CLASS)

        if self.instance and self.instance.type_id:
            self.fields["type_nom"].initial = ""
        if self.instance and self.instance.pk:
            self.fields["est_structure"].initial = bool(self.instance.nom_structure)

    def clean(self):
        cleaned = super().clean()
        type_nom = cleaned.get("type_nom", "").strip()
        self._new_type_name = type_nom
        type_obj = cleaned.get("type")

        if not type_obj and not type_nom:
            self.add_error(
                "type", "Sélectionnez un type existant ou créez-en un nouveau."
            )
        elif (
            type_obj
            and type_nom
            and _normalize_name(type_nom) == _normalize_name(type_obj.nom)
        ):
            self.add_error(
                "type_nom",
                "Ce type existe déjà : sélectionnez-le dans la liste « Type existant ».",
            )

        est_structure = cleaned.get("est_structure", False)
        nom_structure = cleaned.get("nom_structure", "").strip()
        nom = cleaned.get("nom", "").strip()
        prenom = cleaned.get("prenom", "").strip()
        commune = cleaned.get("commune")

        if est_structure:
            cleaned["nom"] = ""
            cleaned["prenom"] = ""
            if not nom_structure:
                self.add_error("nom_structure", "Renseignez le nom de la structure.")
        else:
            cleaned["nom_structure"] = ""
            if not nom and not prenom:
                self.add_error("nom", "Renseignez au moins un nom ou un prénom.")

        if commune is not None and (nom_structure or nom or prenom):
            candidate_identity = nom_structure or f"{prenom} {nom}".strip()
            queryset = Structure.objects.filter(commune=commune)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            candidate_normalized = _normalize_name(candidate_identity)
            # Comparaison en Python mais chargement limité aux trois colonnes utiles,
            # pour ne pas instancier toutes les fiches (JSON d'horaires inclus) de la commune.
            duplicate = next(
                (
                    row
                    for row in queryset.values_list("nom_structure", "prenom", "nom")
                    if _normalize_name(row[0] or f"{row[1]} {row[2]}".strip())
                    == candidate_normalized
                ),
                None,
            )
            if duplicate is not None:
                dup_nom_structure, dup_prenom, dup_nom = duplicate
                duplicate_display = (
                    dup_nom_structure.strip()
                    or " ".join(
                        part for part in (dup_nom, dup_prenom) if part.strip()
                    )
                    or dup_nom
                )
                self.add_error(
                    "nom_structure" if est_structure else "nom",
                    f"Une fiche « {duplicate_display} » existe déjà dans cette commune.",
                )
        places_disponibles = cleaned.get("places_disponibles")
        if places_disponibles is not None and places_disponibles > 0:
            cleaned["places_non_communique"] = False
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self._new_type_name:
            instance.type, _created = TypeStructure.objects.get_or_create(
                nom=self._new_type_name
            )
        geocode_structure(instance)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean_age_min(self):
        val = self.cleaned_data.get("age_min")
        if val is not None and val < 0:
            raise forms.ValidationError("L'âge ne peut pas être négatif.")
        return val

    def clean_email(self):
        return _normalize_email(self.cleaned_data.get("email", ""))

    def clean_email_direction(self):
        return _normalize_email(self.cleaned_data.get("email_direction", ""))

    def clean_telephone(self):
        return _normalize_phone(self.cleaned_data.get("telephone", ""))

    def clean_tel_direction(self):
        return _normalize_phone(self.cleaned_data.get("tel_direction", ""))

    def clean_age_max(self):
        val = self.cleaned_data.get("age_max")
        if val is not None and val < 0:
            raise forms.ValidationError("L'âge ne peut pas être négatif.")
        return val

    def clean_places_disponibles(self):
        val = self.cleaned_data.get("places_disponibles")
        if val is not None and val < 0:
            raise forms.ValidationError("Le nombre ne peut pas être négatif.")
        return val

    def clean_nb_places_total(self):
        val = self.cleaned_data.get("nb_places_total")
        if val is not None and val < 0:
            raise forms.ValidationError("Le nombre ne peut pas être négatif.")
        return val

    def clean_nb_professionnels(self):
        val = self.cleaned_data.get("nb_professionnels")
        if val is not None and val < 0:
            raise forms.ValidationError("Le nombre ne peut pas être négatif.")
        return val
