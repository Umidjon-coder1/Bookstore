from .base import *
import os
from decouple import config, Csv

DEBUG = False

# Railway injects RAILWAY_PUBLIC_DOMAIN automatically
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

# Add Railway domain automatically if present
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# ── Database ──────────────────────────────────────────────────────────────────
# Railway provides DATABASE_URL; fall back to individual vars
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(_database_url, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='bookstore'),
            'USER': config('DB_USER', default='bookstore_user'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
        }
    }

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Security (keep off HTTPS-only headers until SSL confirmed) ────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# Enable these only after confirming HTTPS on Railway:
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000
