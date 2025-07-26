from django import template
from django.template.loader import render_to_string
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def render_statuses_links(post):
    html = []
    statuses = post.statuses.filter(is_published=True).select_related("client")
    for status in statuses:
        icon_template = f"icon_{status.client.platform.lower()}.html"
        icon_html = render_to_string(icon_template)
        html.append(
            format_html(
                '<a href="{}" title="Post on {}">{}</a>',
                status.url,
                status.client.platform,
                icon_html,
            )
        )
    return format_html("".join(str(h) for h in html))
