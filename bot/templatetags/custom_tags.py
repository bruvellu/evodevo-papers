from django import template
from django.template.loader import render_to_string
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def render_statuses_links(post):
    html = []
    statuses = post.statuses.filter(is_published=True).select_related("client")
    for status in statuses:
        platform = status.client.platform.lower()
        icon_template = f"icon_{platform}.html"
        icon_html = render_to_string(icon_template)
        if platform == "twitter":
            link_template = '<a href="{}" onclick="event.preventDefault(); return false;" title="Post on {} (no longer active)">{}</a>'
        else:
            link_template = '<a href="{}" title="Post on {}">{}</a>'
        html.append(
            format_html(
                link_template,
                status.url,
                status.client.platform,
                icon_html,
            )
        )
    return format_html("".join(str(h) for h in html))
