from django import template
from django.utils.html import format_html
from django.utils.http import urlencode

register = template.Library()


@register.filter
def get_item(mapping, key):
    return mapping.get(key, [])


@register.simple_tag(takes_context=True)
def sort_link(context, col, label):
    filters = context["filters"]
    sort_col = context["sort_col"]
    sort_desc = context["sort_desc"]

    params = {}
    for k, v in filters.items():
        if k not in ("o", "page"):
            params[k] = v

    if sort_col == col:
        params["o"] = f"{col}.asc" if sort_desc else f"{col}.desc"
        rotate = "transform:rotate(180deg)" if not sort_desc else ""
        return format_html(
            '<a class="no-underline text-inherit hover:text-[var(--color-primary-hover)] inline-flex items-center gap-1"'
            ' href="?{}">{} <svg class="w-3 h-3 shrink-0 inline" style="{}" aria-hidden="true">'
            '<use href="/static/img/icons.svg#i-chevron-down"></use></svg></a>',
            urlencode(params),
            label,
            rotate,
        )
    else:
        params["o"] = f"{col}.desc"
        return format_html(
            '<a class="no-underline text-inherit hover:text-[var(--color-primary-hover)]"'
            ' href="?{}">{}</a>',
            urlencode(params),
            label,
        )
