"""
إعدادات مشروع المعاهد - نسخة تجريبية.
نستخدم SQLite فقط لأن الهدف نشر سريع على Render بدون قاعدة بيانات خارجية.
ملاحظة: القرص على Render المجاني غير دائم، لذا البيانات قد تُفقد عند إعادة التشغيل.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-demo-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# في وضع التطوير نسمح بكل المضيفين لتسهيل الاختبار عبر Cursor/Render
if DEBUG and os.environ.get('ALLOW_ALL_HOSTS', 'true').lower() in ('true', '1', 'yes'):
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [
        host.strip()
        for host in os.environ.get(
            'ALLOWED_HOSTS',
            'localhost,127.0.0.1,.onrender.com,.cursorvm.com',
        ).split(',')
        if host.strip()
    ]

# مصادر موثوقة لـ CSRF (مطلوب عند الوصول عبر Cursor/Render بـ HTTPS)
_DEFAULT_CSRF_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.onrender.com',
    'https://*.cursorvm.com',
    'https://*.agent.cvm.dev',
]
_env_csrf_origins = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_env_csrf_origins + _DEFAULT_CSRF_ORIGINS))

# خلف بروكسي HTTPS (Cursor/Render)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# إعدادات الكوكيز لبيئة Cursor (iframe + HTTPS)
# المتصفح يحجب كوكيز CSRF بدون SameSite=None; Secure في هذا السياق
CURSOR_DEV = os.environ.get('CURSOR_DEV', 'true').lower() in ('true', '1', 'yes')
if DEBUG and CURSOR_DEV:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_USE_SESSIONS = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'core.middleware.CursorDevCsrfMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'maahid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_display',
                'core.context_processors.request_helpers',
            ],
        },
    },
]

WSGI_APPLICATION = 'maahid.wsgi.application'

# SQLite فقط - بدون PostgreSQL أو MySQL للتبسيط
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/admin-dashboard/'

# حد بسيط لمحاولات تسجيل الدخول
LOGIN_THROTTLE_MAX_ATTEMPTS = 5
LOGIN_THROTTLE_WINDOW_MINUTES = 15

SESSION_COOKIE_AGE = 86400  # 24 ساعة
