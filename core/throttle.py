from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import LoginAttempt


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def is_login_throttled(request):
    """التحقق من تجاوز حد محاولات تسجيل الدخول."""
    ip = get_client_ip(request)
    window = timedelta(minutes=settings.LOGIN_THROTTLE_WINDOW_MINUTES)
    since = timezone.now() - window
    failed_count = LoginAttempt.objects.filter(
        ip_address=ip,
        successful=False,
        attempted_at__gte=since,
    ).count()
    return failed_count >= settings.LOGIN_THROTTLE_MAX_ATTEMPTS


def record_login_attempt(request, identifier='', successful=False):
    LoginAttempt.objects.create(
        ip_address=get_client_ip(request),
        identifier=identifier,
        successful=successful,
    )
