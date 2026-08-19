from django import forms

from .models import JOURS_SEM, Structure, TypeStructure


JOURS_SEM_DICT = dict(JOURS_SEM)

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


class StructureForm(forms.ModelForm):
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

    def clean(self):
        cleaned = super().clean()
        type_nom = cleaned.get("type_nom", "").strip()
        self._new_type_name = type_nom
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self._new_type_name:
            instance.type, _created = TypeStructure.objects.get_or_create(
                nom=self._new_type_name
            )
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def clean_age_min(self):
        val = self.cleaned_data.get("age_min")
        if val is not None and val < 0:
            raise forms.ValidationError("L'âge ne peut pas être négatif.")
        return val

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
