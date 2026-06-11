import os

# ── Import base WITHOUT triggering decouple in Railway ────────────────────────
# Patch env vars before base.py decouple calls execute
os.environ.setdefault('SECRET_KEY', os.environ.get('SECRET_KEY', 'fallback-insecure-key-change-me'))
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('ALLOWED_HOSTS', '*')
os.environ.setdefault('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
os.environ.setdefault('EMAIL_HOST', 'smtp.gmail.com')
os.environ.setdefault('EMAIL_PORT', '587')
os.environ.setdefault('EMAIL_USE_TLS', 'True')
os.environ.setdefault('EMAIL_HOST_USER', '')
os.environ.setdefault('EMAIL_HOST_PASSWORD', '')
os.environ.setdefault('DEFAULT_FROM_EMAIL', 'noreply@bookstore.com')
os.environ.setdefault('CELERY_BROKER_URL', 'redis://localhost:6379/0')
os.environ.setdefault('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
os.environ.setdefault('STRIPE_PUBLIC_KEY', '')
os.environ.setdefault('STRIPE_SECRET_KEY', '')
os.environ.setdefault('STRIPE_WEBHOOK_SECRET', '')
os.environ.setdefault('PAYPAL_CLIENT_ID', '')
os.environ.setdefault('PAYPAL_CLIENT_SECRET', '')
os.environ.setdefault('PAYPAL_MODE', 'sandbox')
os.environ.setdefault('SITE_URL', 'http://localhost:8000')

from .base import *

DEBUG = False

# ── Secret key ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key-change-me')

# ── Allowed hosts ─────────────────────────────────────────────────────────────
ALLOWED_HOSTS = ['*']
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if _railway_domain:
    ALLOWED_HOSTS = ['*', _railway_domain]

# ── CSRF trusted origins ──────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = ['https://*.railway.app', 'https://*.up.railway.app']
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_domain}')

# ── Database ──────────────────────────────────────────────────────────────────
# Railway PostgreSQL: try DATABASE_PUBLIC_URL first (external), then DATABASE_URL (internal).
# Fall back to SQLite if neither is set.
import dj_database_url as _dj_db_url

_database_url = (
    os.environ.get('DATABASE_PUBLIC_URL', '')   # Railway public/external URL
    or os.environ.get('DATABASE_URL', '')        # Railway internal URL
)

# Log which URL is being used (without password)
if _database_url:
    _safe = _database_url.split('@')[-1] if '@' in _database_url else _database_url
    print(f">>> DB URL host: {_safe}")

if _database_url:
    DATABASES = {
        'default': _dj_db_url.parse(_database_url, conn_max_age=600, ssl_require=False)
    }
else:
    print(">>> No DATABASE_URL found — using SQLite fallback")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/app/db.sqlite3',
        }
    }

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use CompressedStaticFilesStorage (NOT Manifest) to avoid ValueError
# when a template references a static file not in the manifest
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ── Cloudinary media storage ──────────────────────────────────────────────────
_cloudinary_url = os.environ.get('CLOUDINARY_URL', '')
if _cloudinary_url:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api

    cloudinary.config(cloudinary_url=_cloudinary_url)

    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']

    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
