from django import forms

from .models import FeedbackReport

INPUT_CLASSES = (
    "block w-full px-4 py-3 text-[length:var(--fs-base)] font-sans "
    "text-[var(--color-text)] bg-[var(--color-surface)] "
    "border border-[var(--color-border-strong)] rounded-[var(--radius-md)] "
    "min-h-[2.75rem] hover:border-[var(--color-primary)] focus:outline-none "
    "focus:border-[var(--color-primary)] "
    "focus:shadow-[0_0_0_3px_var(--color-focus-ring)] "
    "placeholder:text-[var(--color-text-subtle)] placeholder:opacity-100 "
    "transition-[border-color,box-shadow,background] duration-200"
)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackReport
        fields = ["type", "page_declaree", "message"]
        labels = {
            "type": "Type de signalement",
            "page_declaree": "Page concernée",
            "message": "Votre message",
        }
        help_texts = {
            "page_declaree": (
                "Facultatif. Pré-remplie avec la page où vous étiez. "
                "Modifiez-la si le problème concerne une autre page."
            ),
            "message": "Décrivez le problème ou votre remarque (10 à 2000 caractères).",
        }
        widgets = {
            "type": forms.Select(attrs={"class": INPUT_CLASSES}),
            "page_declaree": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "maxlength": "500",
                    "autocomplete": "off",
                    "spellcheck": "false",
                    "placeholder": "/structures/ par exemple",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": "5",
                    "maxlength": "2000",
                    "placeholder": "Que s'est-il passé ? Que cherchiez-vous à faire ?",
                }
            ),
        }

    def clean_page_declaree(self) -> str:
        value = (self.cleaned_data.get("page_declaree") or "").strip()
        if len(value) > 500:
            raise forms.ValidationError("Cette adresse de page est trop longue.")
        return value

    def clean_message(self) -> str:
        value = (self.cleaned_data.get("message") or "").strip()
        if len(value) < 10:
            raise forms.ValidationError(
                "Votre message est trop court (10 caractères minimum)."
            )
        if len(value) > 2000:
            raise forms.ValidationError(
                "Votre message est trop long (2000 caractères maximum)."
            )
        return value
