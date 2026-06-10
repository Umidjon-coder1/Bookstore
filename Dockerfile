FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles /app/logs

# Fix CRLF line endings in entrypoint.sh (safe even if already LF)
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
