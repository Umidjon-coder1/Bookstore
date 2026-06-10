import os
from django.core.wsgi import get_wsgi_application

# Respect DJANGO_SETTINGS_MODULE from environment (set by Railway / Heroku);
# fall back to production so `gunicorn` always uses the right settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
