#!/bin/sh
set -e

export DJANGO_SETTINGS_MODULE=config.settings.production

echo ">>> DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo ">>> DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo YES || echo NO)"
echo ">>> PORT: ${PORT:-8000}"

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting gunicorn on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --timeout 120 \
    --log-level info
