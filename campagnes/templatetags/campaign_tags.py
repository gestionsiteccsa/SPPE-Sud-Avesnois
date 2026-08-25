from django import template

from campagnes.services.campaign import FIELD_LABELS

register = template.Library()


@register.filter
def field_label(field_name: str) -> str:
    """Libellé français d'un champ modifiable d'une fiche."""
    return FIELD_LABELS.get(field_name, field_name)