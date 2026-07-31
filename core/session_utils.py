from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings


def session_query_params(request):
    """معاملات URL اللازمة للحفاظ على الجلسة عبر بروكسي Cursor."""
    params = {}
    ingress = request.GET.get('_ingress_token') or request.POST.get('_ingress_token')
    if ingress:
        params['_ingress_token'] = ingress
    if settings.DEBUG and getattr(settings, 'CURSOR_DEV', False):
        sess_key = request.session.session_key
        if sess_key:
            params['sess'] = sess_key
    return params


def append_query_params(url, params):
    """إضافة معاملات إلى رابط مع الحفاظ على الموجود."""
    if not params:
        return url
    parsed = urlparse(url)
    existing = parse_qs(parsed.query, keep_blank_values=True)
    for key, value in params.items():
        existing[key] = [str(value)]
    new_query = urlencode(existing, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def redirect_url(request, url):
    """بناء رابط إعادة توجيه مع معاملات الجلسة."""
    request.session.save()
    return append_query_params(url, session_query_params(request))
