from .base import *
import os

DEBUG = False

# ── Secret key ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-insecure-key-change-me')

# ── Allowed hosts ─────────────────────────────────────────────────────────────
_allowed = os.environ.get('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# ── Database ──────────────────────────────────────────────────────────────────
# Railway PostgreSQL plugin injects DATABASE_URL automatically.
# Fall back to SQLite so the app still starts if no DB plugin is attached yet.
_database_url = os.environ.get('DATABASE_URL', '')
if _database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(_database_url, conn_max_age=600)
    }
else:
    # SQLite fallback — works but data is lost on redeploy.
    # Add a PostgreSQL plugin in Railway to persist data.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/app/db.sqlite3',
        }
    }

# ── Static files ──────────────────────────────────────────────────────────────
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Security ──────────────────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
