from django import template

from core.session_utils import session_query_params

register = template.Library()


@register.simple_tag(takes_context=True)
def qurl(context, **kwargs):
    """بناء query string مع الحفاظ على معاملات الجلسة."""
    request = context['request']
    params = session_query_params(request)
    for key, value in kwargs.items():
        if value not in (None, ''):
            params[key] = value
    if not params:
        return ''
    from urllib.parse import urlencode
    return f'?{urlencode(params)}'
