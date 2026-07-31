from django.conf import settings


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
