from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore

from .session_utils import append_query_params, session_query_params


class CursorDevCsrfMiddleware:
    """
    تعطيل فحص CSRF في بيئة Cursor التجريبية.
    البروكسي/iframe يمنع حفظ كوكيز CSRF في المتصفح،
    لذا نعطّل الفحص في وضع التطوير فقط (DEBUG + CURSOR_DEV).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and getattr(settings, 'CURSOR_DEV', False):
            request._dont_enforce_csrf_checks = True
        return self.get_response(request)


class CursorSessionRedirectMiddleware:
    """
    يُضاف sess لروابط التوجيه بعد حفظ الجلسة.
    يجب أن يكون قبل SessionMiddleware في القائمة.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG and getattr(settings, 'CURSOR_DEV', False):
            if hasattr(request, 'session') and request.session.session_key:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.get('Location', '')
                    if location and location.startswith('/') and 'sess=' not in location:
                        response['Location'] = append_query_params(
                            location,
                            session_query_params(request),
                        )
        return response


class CursorSessionLoadMiddleware:
    """
    يستعيد الجلسة من ?sess= عندما لا تعمل كوكيز المتصفح.
    يجب أن يكون بعد SessionMiddleware في القائمة.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and getattr(settings, 'CURSOR_DEV', False):
            sess_key = request.GET.get('sess') or request.POST.get('sess')
            if sess_key:
                store = SessionStore(session_key=sess_key)
                if store.exists(sess_key):
                    request.session = store
        return self.get_response(request)
