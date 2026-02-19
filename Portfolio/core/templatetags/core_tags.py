from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='tech_badges')
def tech_badges(tech_stack_string):
    """
    Takes a comma-separated string like "Django, Python, React"
    and returns rendered HTML badges.

    Usage in template:
        {{ project.tech_stack|tech_badges }}

    This eliminates the need for {% for %} loops in templates,
    preventing line-wrapping issues with {{ tech }} variables.
    """
    if not tech_stack_string:
        return mark_safe(
            '<span class="text-xs text-gray-500">'
            'No tech stack listed</span>'
        )

    techs = [t.strip() for t in tech_stack_string.split(',') if t.strip()]

    if not techs:
        return mark_safe(
            '<span class="text-xs text-gray-500">'
            'No tech stack listed</span>'
        )

    badges = []
    for tech in techs:
        safe_name = escape(tech)
        badge = (
            f'<span class="text-xs font-semibold text-primary '
            f'bg-primary/10 px-3 py-1 rounded-full border '
            f'border-primary/20">{safe_name}</span>'
        )
        badges.append(badge)

    return mark_safe(' '.join(badges))


@register.filter(name='default_text')
def default_text(value, default=""):
    """
    Safe default filter that works on any field.
    Returns the default if value is empty/None.

    Usage:
        {{ settings.technical_skills_description|default_text:"Fallback text here" }}
    """
    if value:
        return value
    return default


@register.filter(name='paragraphs_with_divider')
def paragraphs_with_divider(text):
    """
    Splits text into paragraphs (by blank lines) and renders them
    with a narrow white/gray divider between each paragraph.

    Usage in template:
        {{ settings.about_description|paragraphs_with_divider }}

    Input (from Django admin textarea):
        "First paragraph here.

        Second paragraph here.

        Third paragraph here."

    Output: Styled <p> tags with thin divider lines between them.
    """
    if not text:
        return ''

    # Split by double newlines (paragraph breaks)
    # Also handle \r\n line endings
    raw = text.replace('\r\n', '\n')
    paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]

    # If no double-newlines found, try single newlines
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in raw.split('\n') if p.strip()]

    if not paragraphs:
        return ''

    divider = (
        '<div class="my-3">'
        '<div class="w-full h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>'
        '</div>'
    )

    parts = []
    for i, para in enumerate(paragraphs):
        safe_text = escape(para)
        parts.append(
            f'<p class="text-white leading-relaxed text-base">{safe_text}</p>'
        )
        if i < len(paragraphs) - 1:
            parts.append(divider)

    return mark_safe('\n'.join(parts))
