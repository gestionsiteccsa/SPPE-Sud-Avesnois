"""Étiquettes de template liées à la Content Security Policy."""
import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

_JSON_SCRIPT_ESCAPES = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}


@register.simple_tag(takes_context=True)
def json_script_nonce(context, value, element_id):
    """Sérialise `value` dans un <script type="application/json"> avec nonce CSP.

    Équivalent du filtre ``json_script`` mais porteur du nonce de la requête,
    pour rester autorisé par une politique script-src stricte.
    """
    nonce = context.get("csp_nonce", "")
    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_JSON_SCRIPT_ESCAPES)
    return format_html(
        '<script id="{}" type="application/json" nonce="{}">{}</script>',
        element_id,
        nonce,
        mark_safe(json_str),
    )
